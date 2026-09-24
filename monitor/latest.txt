# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: MOVER_AVWAP_SCALP
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `449` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 741 | 741 | 705 | 5 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 14701 | 14701 | 14054 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 121412 | 121278 | 167 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 107312 | 107313 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 107091 | 103737 | 3566 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 107328 | 105525 | 1857 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 112346 | 112256 | 121 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 92987 | 92988 | 14 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 107387 | 107410 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 107417 | 103529 | 5085 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 133412 | 139655 | 2524 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 121447 | 102476 | 30890 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 111914 | 111915 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 107313 | 107305 | 14 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 107062 | 106787 | 302 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 108618 | 107030 | 2139 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 106607 | 106694 | 332 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 88477 | 80398 | 8441 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 88843 | 88553 | 330 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 121375 | 121237 | 169 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 93004 | 93001 | 16 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6128 | 6128 | 5943 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 775 | 775 | 500 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 66 | 66 | 61 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 45709 | 45709 | 45639 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 14946 | 14946 | 14267 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 6802 | 6802 | 5717 | 32 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 100165 | 100165 | 89433 | 206 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 51 | 51 | 51 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1736 | 1736 | 1497 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 6298 | 6298 | 6173 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1169 | 1169 | 1143 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1628 | 1628 | 1564 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 331 | 331 | 219 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1342 | 1342 | 1237 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=121278): breakout_not_found=62063, basic_filters_failed=36612, move_not_fresh=13027, breakout_stale=5537, retest_proximity_failed=3394, volume_spike_missing=620, missing_fvg_or_orderblock=19, move_exhausted=3, ema_alignment_reject=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=107313): cls_disabled_merged_into_lsr=107313
- **EVAL::DIVERGENCE_CONTINUATION** (total=103737): cvd_divergence_failed=35018, h1_trend_not_aligned=33488, basic_filters_failed=25292, ema_alignment_reject=7553, retest_proximity_failed=1985, missing_fvg_or_orderblock=401
- **EVAL::FAILED_AUCTION_RECLAIM** (total=105525): auction_not_detected=64463, basic_filters_failed=24449, reclaim_hold_failed=6989, regime_blocked=5272, tail_too_small=4309, rsi_reject=43
- **EVAL::FUNDING_EXTREME** (total=112256): funding_not_extreme=82355, basic_filters_failed=25590, missing_funding_rate=2154, ema_alignment_reject=1262, rsi_reject=565, momentum_reject=163, cvd_divergence_failed=159, missing_fvg_or_orderblock=8
- **EVAL::LIQUIDATION_REVERSAL** (total=92988): cascade_threshold_not_met=65565, basic_filters_failed=25999, cvd_divergence_failed=729, rsi_reject=645, missing_fvg_or_orderblock=34, volume_spike_missing=16
- **EVAL::MA_CROSS_TREND_SHIFT** (total=107410): no_ma_cross=79335, basic_filters_failed=25309, ma_cross_htf_misaligned=2469, ma_cross_cooldown=297
- **EVAL::MEAN_REVERT** (total=103529): no_extension=77675, basic_filters_failed=25854
- **EVAL::MOVER_AVWAP_SCALP** (total=139655): no_avwap_tag=64430, basic_filters_failed=36775, no_mover_leg=22454, avwap_slope_against=9873, avwap_reclaim_no_volume=3439, no_avwap_reclaim=2475, anchor_too_recent=209
- **EVAL::MOVER_TREND_PULLBACK** (total=102476): basic_filters_failed=36691, no_reclaim=34806, mover_run_too_small=26696, no_pullback_tag=4283
- **EVAL::OPENING_RANGE_BREAKOUT** (total=111915): feature_disabled=111915
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=107305): regime_blocked=89159, breakout_not_found=15589, basic_filters_failed=2421, adx_reject=121, ema_alignment_reject=15
- **EVAL::QUIET_COMPRESSION_BREAK** (total=106787): compression_not_detected=54079, regime_blocked=23390, basic_filters_failed=22018, breakout_not_detected=6433, volume_confirmation_failed=752, rsi_reject=99, missing_fvg_or_orderblock=16
- **EVAL::RANGE_FADE** (total=107030): no_range_edge=81173, basic_filters_failed=25857
- **EVAL::SR_FLIP_RETEST** (total=106694): flip_close_not_confirmed=65253, basic_filters_failed=24425, regime_blocked=5255, h1_break_not_confirmed=3510, retest_out_of_zone=3408, long_break_volume_thin=3206, reclaim_hold_failed=1093, long_acceptance_not_held=217, ema_alignment_reject=123, wick_quality_failed=96, whipsaw_flip=82, missing_fvg_or_orderblock=26
- **EVAL::STANDARD** (total=80398): basic_filters_failed=19403, adx_reject=18221, momentum_reject=13708, macd_reject=11099, sweeps_not_detected=10009, ema_alignment_reject=5487, htf_poi_unanchored=2149, rsi_reject=176, invalid_sl_geometry=143, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=88553): h1_trend_not_aligned=37418, h1_pullback_not_confirmed=17574, ema_alignment_reject=12430, basic_filters_failed=7685, ema_not_tested_prev=4192, no_ema_reclaim_close=3580, body_conviction_fail=2072, rsi_reject=1803, prev_already_below_emas=688, no_prev_low_break=326, prev_already_above_emas=319, no_prev_high_break=263, momentum_flat=123, ema21_not_tagged=49, missing_fvg_or_orderblock=26, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=121237): breakout_not_found=67781, basic_filters_failed=36609, move_not_fresh=9605, breakout_stale=4912, retest_proximity_failed=1911, volume_spike_missing=365, move_exhausted=44, missing_fvg_or_orderblock=10
- **EVAL::WHALE_MOMENTUM** (total=93001): momentum_reject=74358, recent_ticks_insufficient=12058, basic_filters_failed=6585

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=79): execution:overextended=79
- **DIVERGENCE_CONTINUATION** (total=1145): setup_compat:regime_VOLATILE_UNSUITABLE=1074, setup_compat:regime_BREAKOUT_EXPANSION=71
- **FAILED_AUCTION_RECLAIM** (total=2264): execution:overextended=1543, setup_compat:regime_STRONG_TREND=674, setup_compat:regime_VOLATILE_UNSUITABLE=46, context_floor=1
- **FUNDING_EXTREME_SIGNAL** (total=647): execution:trigger_not_confirmed=647
- **LIQUIDATION_REVERSAL** (total=66): execution:trigger_not_confirmed=66
- **LIQUIDITY_SWEEP_REVERSAL** (total=10737): execution:overextended=5218, execution:trigger_not_confirmed=3352, setup_compat:regime_STRONG_TREND=2167
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=1, execution:overextended=1, setup_compat:regime_VOLATILE_UNSUITABLE=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=5175): setup_compat:regime_WEAK_TREND=1858, execution:overextended=1674, setup_compat:regime_STRONG_TREND=1643
- **MOVER_AVWAP_SCALP** (total=4572): execution:overextended=3834, execution:trigger_not_confirmed=565, entry_quality=173
- **MOVER_TREND_PULLBACK** (total=33148): execution:trigger_not_confirmed=21403, execution:overextended=10193, entry_quality=1552
- **RANGE_FADE** (total=2847): setup_compat:regime_STRONG_TREND=1342, setup_compat:regime_WEAK_TREND=1083, execution:overextended=246, setup_compat:regime_VOLATILE_UNSUITABLE=175, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=1596): setup_compat:regime_CLEAN_RANGE=910, setup_compat:regime_DIRTY_RANGE=586, setup_compat:regime_VOLATILE_UNSUITABLE=74, entry_quality=26
- **VOLUME_SURGE_BREAKOUT** (total=56): execution:overextended=56
- **WHALE_MOMENTUM** (total=743): execution:trigger_not_confirmed=643, execution:overextended=100

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 406633 | 60.4% |
| QUIET | 102668 | 15.3% |
| TRENDING_DOWN | 87783 | 13.0% |
| TRENDING_UP | 39781 | 5.9% |
| VOLATILE | 36347 | 5.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **85**
- Average confidence gap to threshold: **9.59** (samples=85) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=13, TRXUSDT=11, HBARUSDT=11, AAVEUSDT=11, WLDUSDT=8, PUMPUSDT=8, TAOUSDT=7, ETHUSDT=6, ETCUSDT=5, ASTERUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 12 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 11 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 162 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 20 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 95 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 8 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 9 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 15 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 294 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 26 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 457 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1706 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 50 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2937 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 144 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 7 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 36 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 27 |
| WHALE_MOMENTUM | filtered | min_confidence | 9 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 12 | 54.91 | 62.67 | 7.76 | 19.80 | 18.15 | 20.00 | 4.75 | 22.25 |
| BREAKDOWN_SHORT | kept | 11 | 67.80 | 65.00 | -2.80 | 21.08 | 18.55 | 20.00 | 4.50 | 8.47 |
| DIVERGENCE_CONTINUATION | filtered | 162 | 49.96 | 64.06 | 14.10 | 20.56 | 19.35 | 18.20 | 2.75 | 17.98 |
| DIVERGENCE_CONTINUATION | kept | 20 | 69.40 | 65.00 | -4.40 | 18.90 | 18.19 | 19.59 | 4.20 | 3.73 |
| FAILED_AUCTION_RECLAIM | filtered | 95 | 28.46 | 60.11 | 31.65 | 21.21 | 18.12 | 20.00 | 1.21 | 28.16 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.75 | 65.00 | -1.75 | 20.55 | 17.35 | 20.00 | 1.00 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 57.70 | 61.00 | 3.30 | 20.41 | 14.00 | 17.00 | 7.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 9 | 72.10 | 65.00 | -7.10 | 19.79 | 14.67 | 17.00 | 2.67 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 9 | 55.62 | 64.11 | 8.49 | 20.32 | 20.00 | 18.33 | 2.44 | 14.56 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 15 | 68.79 | 65.00 | -3.79 | 20.92 | 19.23 | 18.80 | 1.67 | 0.17 |
| MOVER_AVWAP_SCALP | filtered | 324 | 55.58 | 60.35 | 4.77 | 20.00 | 15.16 | 15.80 | 4.17 | 13.16 |
| MOVER_AVWAP_SCALP | kept | 457 | 76.78 | 65.00 | -11.78 | 19.58 | 15.58 | 15.80 | 4.06 | 7.27 |
| MOVER_TREND_PULLBACK | filtered | 1756 | 58.08 | 64.30 | 6.22 | 19.96 | 18.47 | 15.80 | 4.07 | 16.98 |
| MOVER_TREND_PULLBACK | kept | 2937 | 76.44 | 65.00 | -11.44 | 19.79 | 18.03 | 15.80 | 4.05 | 3.87 |
| QUIET_COMPRESSION_BREAK | filtered | 171 | 53.74 | 64.72 | 10.98 | 21.17 | 18.13 | 20.00 | 0.00 | 0.09 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 72.93 | 65.00 | -7.93 | 21.75 | 19.10 | 20.00 | 0.00 | 2.77 |
| SR_FLIP_RETEST | kept | 9 | 70.63 | 65.00 | -5.63 | 19.74 | 20.00 | 15.87 | 2.61 | -1.10 |
| TREND_PULLBACK_EMA | kept | 7 | 71.03 | 65.00 | -6.03 | 21.06 | 19.27 | 18.21 | 4.93 | 5.86 |
| VOLUME_SURGE_BREAKOUT | filtered | 36 | 56.85 | 64.33 | 7.48 | 20.41 | 14.00 | 20.00 | 3.97 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 27 | 79.99 | 65.00 | -14.99 | 18.22 | 18.64 | 20.00 | 4.65 | 0.33 |
| WHALE_MOMENTUM | filtered | 13 | 42.88 | 62.23 | 19.35 | 21.56 | 15.43 | 17.00 | 0.00 | 25.19 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 12 | 54.91 | 20.33 | 15.00 | 12.00 | 13.25 | 5.00 | 6.83 | 4.75 |
| BREAKDOWN_SHORT | kept | 11 | 67.80 | 19.91 | 14.36 | 14.18 | 11.00 | 5.00 | 7.32 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 162 | 49.96 | 22.09 | 9.33 | 6.04 | 14.18 | 4.85 | 8.71 | 2.75 |
| DIVERGENCE_CONTINUATION | kept | 20 | 69.40 | 25.00 | 8.20 | 9.75 | 13.00 | 5.15 | 8.42 | 4.20 |
| FAILED_AUCTION_RECLAIM | filtered | 95 | 28.46 | 18.09 | 18.00 | 8.49 | 14.00 | 7.69 | 2.55 | 1.21 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.75 | 17.00 | 18.00 | 7.50 | 14.00 | 9.25 | 3.00 | 1.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 57.70 | 17.00 | 20.00 | 6.00 | 12.00 | 10.00 | 0.70 | 7.00 |
| FUNDING_EXTREME_SIGNAL | kept | 9 | 72.10 | 25.00 | 20.00 | 3.00 | 9.56 | 5.39 | 6.49 | 2.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 9 | 55.62 | 23.22 | 14.89 | 5.00 | 13.33 | 5.00 | 6.29 | 2.44 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 15 | 68.79 | 22.87 | 14.00 | 5.40 | 13.67 | 5.00 | 6.33 | 1.67 |
| MOVER_AVWAP_SCALP | filtered | 324 | 55.58 | 17.98 | 18.27 | 11.26 | 14.99 | 6.10 | 5.99 | 4.17 |
| MOVER_AVWAP_SCALP | kept | 457 | 76.78 | 20.05 | 18.57 | 12.43 | 14.08 | 6.78 | 9.06 | 4.06 |
| MOVER_TREND_PULLBACK | filtered | 1756 | 58.08 | 17.76 | 18.17 | 7.71 | 13.03 | 5.99 | 9.27 | 4.07 |
| MOVER_TREND_PULLBACK | kept | 2937 | 76.44 | 20.32 | 18.16 | 7.93 | 13.79 | 6.85 | 9.32 | 4.05 |
| QUIET_COMPRESSION_BREAK | filtered | 171 | 53.74 | 20.70 | 14.63 | 10.96 | 14.00 | 6.27 | 4.19 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 72.93 | 22.33 | 17.33 | 12.50 | 14.50 | 6.33 | 6.17 | 0.00 |
| SR_FLIP_RETEST | kept | 9 | 70.63 | 23.22 | 16.89 | 3.33 | 14.33 | 5.00 | 6.00 | 2.61 |
| TREND_PULLBACK_EMA | kept | 7 | 71.03 | 14.86 | 18.00 | 7.93 | 14.43 | 8.79 | 9.24 | 4.93 |
| VOLUME_SURGE_BREAKOUT | filtered | 36 | 56.85 | 17.89 | 14.33 | 14.33 | 12.33 | 3.61 | 8.38 | 3.97 |
| VOLUME_SURGE_BREAKOUT | kept | 27 | 79.99 | 18.78 | 16.89 | 12.22 | 13.78 | 5.19 | 9.38 | 4.65 |
| WHALE_MOMENTUM | filtered | 13 | 42.88 | 20.08 | 8.00 | 10.85 | 14.00 | 7.15 | 8.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 12 | 54.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 11 | 67.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 162 | 49.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 20 | 69.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 95 | 28.46 | 0.00 | 0.00 | 0.00 | 0.00 | 1.26 | 0.00 | 0.00 | 0.00 | **1.26** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 57.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 9 | 72.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 9 | 55.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 15 | 68.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 324 | 55.58 | 0.94 | 0.00 | 0.00 | 0.00 | 3.93 | 0.90 | 0.00 | 1.85 | **7.62** |
| MOVER_AVWAP_SCALP | kept | 457 | 76.78 | 0.05 | 0.00 | 0.02 | 0.00 | 0.03 | 0.50 | 0.00 | 0.38 | **0.98** |
| MOVER_TREND_PULLBACK | filtered | 1756 | 58.08 | 0.01 | 0.00 | 0.92 | 0.00 | 0.52 | 0.33 | 0.00 | 0.00 | **1.78** |
| MOVER_TREND_PULLBACK | kept | 2937 | 76.44 | 0.01 | 0.00 | 0.14 | 0.00 | 0.02 | 0.02 | 0.00 | 0.00 | **0.19** |
| QUIET_COMPRESSION_BREAK | filtered | 171 | 53.74 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.32 | **0.32** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 72.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| SR_FLIP_RETEST | kept | 9 | 70.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 7 | 71.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 36 | 56.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 27 | 79.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 13 | 42.88 | 0.00 | 0.00 | 0.00 | 0.00 | 4.98 | 0.00 | 0.00 | 0.00 | **4.98** |

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
- Outcomes recorded: **109441 held of 295144 seen** across 21 strategies; 2500 cells past the sample floor; **1126 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 38227 | 572/37655/0 | 43% | -0.18 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.16R) |
| MOVER_AVWAP_SCALP | 13666 | 198/13468/0 | 41% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 8258 | 108/8150/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6971 | 40/6931/0 | 50% | -0.01 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5954 | 0/0/5954 | 42% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.84R) |
| TREND_PULLBACK_EMA | 5471 | 24/5447/0 | 44% | -0.18 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 5102 | 0/0/5102 | 37% | -0.10 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.70R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.17R) |
| QUIET_COMPRESSION_BREAK | 4964 | 286/4678/0 | 48% | -0.11 | ASIA/RANGE/NORMAL/BTC_FALLING (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4658 | 0/0/4658 | 34% | -0.41 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3329 | 63/3266/0 | 37% | -0.37 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2183 | 30/2153/0 | 49% | -0.13 | LONDON/MARKDOWN/EXPANDED/BTC_RISING (+1.23R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1869 | 2/1867/0 | 33% | -0.42 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1798 | 0/1798/0 | 40% | -0.06 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1192 | 10/1182/0 | 48% | -0.22 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 876 | 0/0/876 | 54% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.16R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 719 | 0/719/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 533 | 47/486/0 | 33% | -0.32 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 62 | 6/56/0 | 45% | -0.06 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 145 | 28% / -0.55R | 145 | 47% / -0.19R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 449 | 44% / -0.23R | 449 | 55% / -0.04R | +0.19 | **ATR** |
| BREAKDOWN_SHORT | 40 | 38% / -0.21R | 40 | 42% / -0.09R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1086 | 44% / -0.19R | 1086 | 50% / -0.08R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 135 | 49% / -0.26R | 135 | 50% / -0.17R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5922 | 50% / -0.10R | 5922 | 54% / -0.01R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 754 | 43% / -0.18R | 754 | 46% / -0.10R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 650 | 50% / -0.21R | 650 | 55% / -0.13R | +0.07 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 98 | 40% / -0.09R | 98 | 47% / -0.06R | +0.03 | **ATR** |
| RANGE_FADE | 36 | 39% / -0.21R | 36 | 42% / -0.24R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 647 | 51% / -0.06R | 647 | 56% / -0.04R | +0.02 | **ATR** |
| MEAN_REVERT | 157 | 54% / -0.07R | 157 | 52% / -0.06R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 791 | 45% / -0.16R | 791 | 45% / -0.17R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 20 | 40% / -0.15R | 20 | 40% / -0.14R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8486 | 29% | -0.25R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1086 | 48% | -0.07R | 194 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 61 | 51% | -0.05R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 762 | 36% / -0.12R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7583 | 36% / -0.16R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1450 | 35% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 603 | 35% / -0.13R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 733 | 41% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 601 | 38% / -0.06R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 650 | 42% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 138 | 28% / -0.43R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 190 | 30% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 131 | 56% / +0.13R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 73 | 44% / -0.14R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 28 | 36% / +0.13R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 138 | 36% / -0.38R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 29 | 17% / -0.49R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 58 · alerting: **0** · boot grace active: True

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 496462 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 10 arms current, none stalled; covering 730/730 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 20 arms current, none stalled; covering 1014/1014 signals (100%) | 0 |
| auto_dispatch | ok | placed=0 rejected=0 skipped=0 over 0 fan-out(s) to a keyed roster (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| binance_ip_weight | ok | peak 176/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 84210.90 | 0 |
| candle_coverage | ok | 81/81 symbols with ≥20 15m candles, 81/81 updated within 45m [fresh=81; 75 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 427 dup bars, 0 undedupable; ws 0 out-of-order, 75 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +3 / upstream +50 | 0 |
| dark_atr_trail_arms | ok | boot grace (1 dark ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 43 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/3)) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | boot grace (2 of 55 open dark rows are not being advanced (worst: STRKUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 1/120)) | 0 |
| dark_sar_arms | ok | boot grace (1 dark SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 41 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/3)) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 124043 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | boot grace (MEAN_REVERT realized−counterfactual=+0.64R (bound 0.3) (streak 1/6)) | 0 |
| emission_controller | ok | last cycle 1271s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | boot grace (2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×655]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 1/6)) | 0 |
| entry_quality_effective | ok | only 3 candidates evaluated — too few to judge | 0 |
| firestore_read_budget | ok | 1,585 reads/day of 50,000 (engine); top site keystore.roster_doc at 370/day | 0 |
| footprint_bars | ok | 1080 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +276 | 0 |
| indicator_cache_key | ok | 104 frozen value(s) avoided; 9878 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.14R over n=2153 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +51 / upstream +276 | 0 |
| mover_admission_metadata | ok | 907 symbols known, 201 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3169 rows held, 1764641 evicted (sampled: execution:trigger_not_confirmed 400/652069, execution:overextended 400/587380, setup_compat:regime_STRONG_TREND 400/259232) | 0 |
| price_action_lane | ok | 20246 evaluated, 6 emitted; layer1 6 stamped / 0 blind; cooldown=1508, delta_opposed=2551, no_footprint=7747, no_sweep=6003, rr_below_floor=2431 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=719 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +319 / upstream +276 | 0 |
| sar_alignment_crosscheck | ok | 0/66 disagreed (0.0%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +276 | 0 |
| sar_hold_arm | ok | 1825 held arms settled, 175 unscored, 17 still walking (15 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | boot grace (21/34 unfetchable (62%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, ADAUSDT, AKEUSDT, AVAXUSDT, DASHUSDT +8 more (streak 1/6)) | 0 |
| sar_live_arms | ok | 17 arms current, none stalled; covering 1012/1012 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | boot grace (0 verdicts produced while 434 records await one (13 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12)) | 0 |
| scan_cycle | ok | last 12.12s, worst 33.25s over 262 lifetime cycles; lifetime 0 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.12s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 9152 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 7m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (8.08s to run, worst 21.11s), 2 overrun(s) of 105 cycles, TTL 900s; slowest positions_diag=3.0s, tickers=2.55s, signals=1.51s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +2 / upstream +276 | 0 |
| structural_snap | ok | 5472/5472 measured, 25 blind, 0 levels moved (refusals: none) | 0 |
| structural_veto_lane | ok | only 0 rows stamped yet | 0 |
| suppression_audit | ok | output +276 / upstream +50 | 0 |
| tuned_variants | ok | seen=3 stamped=1 skipped=2, residue 0 (none recorded) | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3610374`
- `Path funnel` emissions: `78`
- `Regime distribution` emissions: `78`
- `QUIET_SCALP_BLOCK` events: `85`
- `confidence_gate` events: `6086`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 14847 | 14847 | 14847 | 0 |
| futures_aggtrade | 5 | 5888 | 12949 | 13111 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=562158] state[populated=562158] buckets[many=562158] sources[none] quality[none]
- funding_rate: presence[absent=71837, present=490321] state[empty=71837, populated=490321] buckets[few=490321, none=71837] sources[none] quality[none]
- liquidation_clusters: presence[absent=292939, present=269219] state[empty=292939, populated=269219] buckets[few=213305, none=292939, some=55914] sources[none] quality[none]
- oi_snapshot: presence[absent=65234, present=496924] state[empty=65234, populated=496924] buckets[few=51, many=496682, none=65234, some=191] sources[none] quality[none]
- order_book: presence[absent=153024, present=409134] state[populated=409134, unavailable=153024] buckets[few=409134, none=153024] sources[book_ticker=409134, unavailable=153024] quality[none=153024, top_of_book_only=409134]
- orderblocks: presence[absent=562158] state[empty=562158] buckets[none=562158] sources[measured_dark=562158] quality[none]
- recent_ticks: presence[present=562158] state[populated=562158] buckets[many=562158] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.9697810411453247` sec
- Median create→first breach: `3312.9208854436874` sec
- Median create→terminal: `3313.379495382309` sec
- Median first breach→terminal: `7.402896881103516e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 1.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 1.9}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 2.2099841320741875 | 2.3726116144781932 | 0.9345821019092251 | 0 | 2 |
| MOVER_AVWAP_SCALP | 5 | 5 | 3.7894323200988747 | 2.970600000000018 | 1.2756454319325563 | 4 | 1 |
| MOVER_TREND_PULLBACK | 43 | 43 | 3.46625371702871 | 3.0 | 1.1554179056762368 | 28 | 15 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.2775558034992422 | 1.381897679919817 | 0.9200873447752353 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.2388 | 25675.276827454567 | 25675.6490650177 |
| MOVER_AVWAP_SCALP | 5 | 5 | 80.0 | 0.0 | 80.0 | 0.0 | 2.5983 | 5359.416049003601 | 5360.221708059311 |
| MOVER_TREND_PULLBACK | 43 | 43 | 30.2 | 46.5 | 30.2 | 0.0 | -0.1956 | 2915.51043009758 | 2915.5104990005493 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | 0.1427 | 19763.76298391819 | 19763.76305091381 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1169 | 2 | 1143 | 0.0 | 0.0 | None | None | 26 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1628 | 5 | 1564 | 0.0 | 0.0 | None | None | 64 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-55`
- Gating Δ: `106927`
- No-generation Δ: `1178660`
- Fast failures Δ: `1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.2043, "current_avg_pnl": 1.2388, "current_win_rate": 50.0, "previous_avg_pnl": 1.4431, "previous_win_rate": 33.3, "win_rate_delta": 16.7}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -1.8998, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 1.8998, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MEAN_REVERT": {"avg_pnl_delta": -0.9938, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.9938, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.778, "current_avg_pnl": 2.5983, "current_win_rate": 80.0, "previous_avg_pnl": -0.1797, "previous_win_rate": 16.7, "win_rate_delta": 63.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.6894, "current_avg_pnl": -0.1956, "current_win_rate": 30.2, "previous_avg_pnl": 0.4938, "previous_win_rate": 40.0, "win_rate_delta": -9.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0936, "current_avg_pnl": 0.1427, "current_win_rate": 25.0, "previous_avg_pnl": 0.0491, "previous_win_rate": 16.7, "win_rate_delta": 8.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 19, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -18, "geometry_changed_delta": 0, "geometry_preserved_delta": -125, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
