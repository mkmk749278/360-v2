# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::WHALE_MOMENTUM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `2250` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 123 | 123 | 122 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9038 | 9038 | 8263 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 70179 | 70187 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 61782 | 61792 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 61600 | 58238 | 3542 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 61811 | 58895 | 3028 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 72956 | 72799 | 184 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 63048 | 63056 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 61930 | 61957 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 76039 | 77534 | 1322 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 70192 | 63749 | 12266 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 71285 | 71291 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 61799 | 61797 | 11 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 61548 | 61078 | 513 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 59853 | 57780 | 3727 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 51588 | 49043 | 2711 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 51755 | 51458 | 320 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 70164 | 70170 | 10 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 63063 | 63068 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 8866 | 8866 | 6861 | 14 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 553 | 553 | 485 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13799 | 13799 | 13798 | 1 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 8 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3058 | 3058 | 3056 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 27657 | 27657 | 24971 | 11 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 70 | 70 | 70 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2134 | 2134 | 1824 | 7 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 12696 | 12696 | 10110 | 10 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1273 | 1273 | 1219 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 54 | 54 | 12 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=70187): breakout_not_found=33625, basic_filters_failed=18690, move_not_fresh=13646, breakout_stale=2750, retest_proximity_failed=791, insufficient_candles=497, volume_spike_missing=188
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=61792): cls_disabled_merged_into_lsr=61792
- **EVAL::DIVERGENCE_CONTINUATION** (total=58238): cvd_divergence_failed=18763, h1_trend_not_aligned=17334, basic_filters_failed=14268, ema_alignment_reject=6271, retest_proximity_failed=1015, missing_fvg_or_orderblock=587
- **EVAL::FAILED_AUCTION_RECLAIM** (total=58895): auction_not_detected=24441, basic_filters_failed=14184, reclaim_hold_failed=12255, tail_too_small=7369, regime_blocked=646
- **EVAL::FUNDING_EXTREME** (total=72799): funding_not_extreme=53536, basic_filters_failed=16225, ema_alignment_reject=2125, rsi_reject=537, cvd_divergence_failed=222, momentum_reject=105, insufficient_candles=22, missing_funding_rate=14, missing_fvg_or_orderblock=13
- **EVAL::LIQUIDATION_REVERSAL** (total=63056): cascade_threshold_not_met=46243, basic_filters_failed=16076, insufficient_candles=277, cvd_divergence_failed=239, rsi_reject=208, volume_spike_missing=12, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=61957): no_ma_cross=46284, basic_filters_failed=14272, ma_cross_cooldown=863, ma_cross_htf_misaligned=538
- **EVAL::MOVER_AVWAP_SCALP** (total=77534): no_mover_leg=25801, no_avwap_tag=24485, basic_filters_failed=18181, avwap_slope_against=6129, insufficient_candles=2697, no_avwap_reclaim=213, avwap_reclaim_no_volume=28
- **EVAL::MOVER_TREND_PULLBACK** (total=63749): mover_run_too_small=33500, basic_filters_failed=18145, no_reclaim=7597, insufficient_candles=2697, no_pullback_tag=1810
- **EVAL::OPENING_RANGE_BREAKOUT** (total=71291): feature_disabled=71291
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=61797): regime_blocked=37358, breakout_not_found=16523, basic_filters_failed=5740, adx_reject=2143, ema_alignment_reject=31, rsi_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=61078): regime_blocked=25040, compression_not_detected=17087, breakout_not_detected=9230, basic_filters_failed=8440, volume_confirmation_failed=907, rsi_reject=319, missing_fvg_or_orderblock=55
- **EVAL::SR_FLIP_RETEST** (total=57780): basic_filters_failed=14173, flip_close_not_confirmed=13362, retest_out_of_zone=7410, long_break_volume_thin=6341, whipsaw_flip=5792, reclaim_hold_failed=4270, long_disabled=3713, wick_quality_failed=1134, regime_blocked=647, long_acceptance_not_held=412, ema_alignment_reject=244, missing_fvg_or_orderblock=172, rsi_reject=110
- **EVAL::STANDARD** (total=49043): momentum_reject=19032, sweeps_not_detected=10045, adx_reject=6406, macd_reject=5835, basic_filters_failed=4519, ema_alignment_reject=2709, invalid_sl_geometry=373, rsi_reject=124
- **EVAL::TREND_PULLBACK** (total=51458): h1_trend_not_aligned=20084, ema_alignment_reject=7774, h1_pullback_not_confirmed=6633, basic_filters_failed=6259, no_ema_reclaim_close=3307, ema_not_tested_prev=3046, body_conviction_fail=2266, rsi_reject=1055, prev_already_below_emas=343, no_prev_low_break=194, prev_already_above_emas=172, no_prev_high_break=145, momentum_flat=83, missing_fvg_or_orderblock=68, momentum_reject=29
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=70170): breakout_not_found=41464, basic_filters_failed=18690, move_not_fresh=6240, breakout_stale=2471, retest_proximity_failed=533, insufficient_candles=497, volume_spike_missing=262, ema_alignment_reject=11, missing_fvg_or_orderblock=2
- **EVAL::WHALE_MOMENTUM** (total=63068): momentum_reject=45679, recent_ticks_insufficient=13194, basic_filters_failed=4195

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 135679 | 38.4% |
| QUIET | 89933 | 25.4% |
| TRENDING_DOWN | 80206 | 22.7% |
| TRENDING_UP | 41127 | 11.6% |
| VOLATILE | 6551 | 1.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **172**
- Average confidence gap to threshold: **11.93** (samples=172) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BCHUSDT=31, TRXUSDT=24, BTCUSDT=22, ONDOUSDT=15, LINKUSDT=15, BZUSDT=14, AVAXUSDT=11, XRPUSDT=11, DOGEUSDT=10, SOXLUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 146 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 6 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 45 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 300 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 26 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 221 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 2 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 363 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1541 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 103 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 60 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 9 |
| SR_FLIP_RETEST | filtered | min_confidence | 390 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 37 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 114 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 43 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 11 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 73.00 | 65.00 | -8.00 | 20.30 | 19.20 | 20.00 | 4.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 152 | 49.70 | 65.00 | 15.30 | 20.69 | 19.66 | 18.35 | 1.73 | 17.98 |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.34 | 65.00 | -3.34 | 20.99 | 19.74 | 18.39 | 1.56 | 3.96 |
| FAILED_AUCTION_RECLAIM | filtered | 326 | 51.85 | 65.00 | 13.15 | 19.68 | 19.38 | 20.00 | 4.59 | 6.00 |
| FAILED_AUCTION_RECLAIM | kept | 221 | 70.63 | 65.00 | -5.63 | 21.07 | 18.76 | 20.00 | 4.33 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.70 | 65.00 | 18.30 | 20.70 | 20.00 | 18.80 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 65.20 | 65.00 | -0.20 | 20.80 | 19.20 | 19.50 | 3.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 2 | 57.70 | 65.00 | 7.30 | 17.10 | 16.00 | 15.80 | 4.50 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 363 | 55.12 | 65.00 | 9.88 | 19.32 | 19.35 | 15.80 | 5.06 | 16.81 |
| MOVER_TREND_PULLBACK | kept | 1541 | 77.45 | 65.00 | -12.45 | 19.91 | 18.72 | 15.80 | 4.34 | 1.68 |
| QUIET_COMPRESSION_BREAK | filtered | 163 | 58.64 | 65.00 | 6.36 | 20.96 | 19.91 | 20.00 | 0.00 | 11.55 |
| QUIET_COMPRESSION_BREAK | kept | 9 | 71.56 | 65.00 | -6.56 | 21.64 | 19.68 | 20.00 | 0.00 | 1.61 |
| SR_FLIP_RETEST | filtered | 427 | 58.36 | 65.00 | 6.64 | 20.31 | 19.81 | 15.57 | 1.40 | 8.79 |
| SR_FLIP_RETEST | kept | 114 | 71.29 | 65.00 | -6.29 | 20.19 | 19.76 | 16.30 | 1.92 | 1.27 |
| TREND_PULLBACK_EMA | filtered | 43 | 60.50 | 65.00 | 4.50 | 19.14 | 19.20 | 17.70 | 5.50 | 20.00 |
| TREND_PULLBACK_EMA | kept | 11 | 87.36 | 65.00 | -22.36 | 21.42 | 20.00 | 15.65 | 5.50 | -2.73 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 58.50 | 65.00 | 6.50 | 18.40 | 20.00 | 20.00 | 4.50 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 73.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 152 | 49.70 | 19.42 | 16.22 | 4.46 | 12.57 | 4.97 | 8.30 | 1.73 |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.34 | 21.80 | 14.67 | 9.33 | 11.76 | 5.16 | 8.64 | 1.56 |
| FAILED_AUCTION_RECLAIM | filtered | 326 | 51.85 | 21.61 | 17.61 | 4.90 | 12.42 | 6.50 | 4.40 | 4.59 |
| FAILED_AUCTION_RECLAIM | kept | 221 | 70.63 | 22.10 | 15.88 | 4.22 | 10.70 | 6.87 | 6.52 | 4.33 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.70 | 25.00 | 8.00 | 3.00 | 17.00 | 10.00 | 3.70 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 65.20 | 25.00 | 14.00 | 3.00 | 9.00 | 2.50 | 8.70 | 3.00 |
| MOVER_AVWAP_SCALP | filtered | 2 | 57.70 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 6.70 | 4.50 |
| MOVER_TREND_PULLBACK | filtered | 363 | 55.12 | 17.03 | 18.00 | 8.06 | 12.62 | 5.64 | 9.40 | 5.06 |
| MOVER_TREND_PULLBACK | kept | 1541 | 77.45 | 19.06 | 18.14 | 7.98 | 14.15 | 5.83 | 9.63 | 4.34 |
| QUIET_COMPRESSION_BREAK | filtered | 163 | 58.64 | 17.39 | 16.53 | 13.14 | 14.09 | 7.52 | 3.08 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 9 | 71.56 | 20.56 | 17.11 | 12.67 | 14.67 | 5.78 | 4.39 | 0.00 |
| SR_FLIP_RETEST | filtered | 427 | 58.36 | 18.93 | 17.13 | 4.93 | 12.71 | 5.25 | 6.80 | 1.40 |
| SR_FLIP_RETEST | kept | 114 | 71.29 | 21.77 | 18.00 | 6.29 | 10.66 | 5.03 | 8.95 | 1.92 |
| TREND_PULLBACK_EMA | filtered | 43 | 60.50 | 17.00 | 18.00 | 7.50 | 14.00 | 8.50 | 10.00 | 5.50 |
| TREND_PULLBACK_EMA | kept | 11 | 87.36 | 24.27 | 18.00 | 7.50 | 14.00 | 8.18 | 9.91 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 58.50 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 2.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 73.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 152 | 49.70 | 0.00 | 0.00 | 0.05 | 0.00 | 1.22 | 0.00 | 0.00 | 0.00 | **1.27** |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | **0.16** |
| FAILED_AUCTION_RECLAIM | filtered | 326 | 51.85 | 0.00 | 0.00 | 3.21 | 0.00 | 1.86 | 0.00 | 0.00 | 0.00 | **5.07** |
| FAILED_AUCTION_RECLAIM | kept | 221 | 70.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 65.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 2 | 57.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 363 | 55.12 | 0.00 | 0.00 | 2.70 | 0.00 | 1.06 | 0.00 | 0.00 | 0.00 | **3.76** |
| MOVER_TREND_PULLBACK | kept | 1541 | 77.45 | 0.00 | 0.00 | 0.65 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **1.68** |
| QUIET_COMPRESSION_BREAK | filtered | 163 | 58.64 | 0.00 | 0.00 | 0.00 | 0.00 | 1.24 | 0.00 | 0.00 | 7.51 | **8.75** |
| QUIET_COMPRESSION_BREAK | kept | 9 | 71.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.74 | 0.00 | 0.00 | 1.87 | **2.61** |
| SR_FLIP_RETEST | filtered | 427 | 58.36 | 0.00 | 0.00 | 0.15 | 0.00 | 1.52 | 0.00 | 0.00 | 2.21 | **3.88** |
| SR_FLIP_RETEST | kept | 114 | 71.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | **0.06** |
| TREND_PULLBACK_EMA | filtered | 43 | 60.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 11 | 87.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 58.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=33 (67.3%) | PREMATURE=9 (18.4%) | NEUTRAL=7 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 24 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 33 | 9 | 7 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 0 | 3 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 3 | 5 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 9 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 13 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 5 | 2 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 33 | 9 | 7 | 26.1 | 10.0 | +0.33 | **KEEP** — net-helping: avg +0.33R/kill across 49 kills (saved 26.1R vs missed 10.0R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `77702`
- `Path funnel` emissions: `45`
- `Regime distribution` emissions: `45`
- `QUIET_SCALP_BLOCK` events: `172`
- `confidence_gate` events: `3424`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 2 | 2055 | 2055 | 2478 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| regime_shift | 4 |
| signal_close | 2 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=275856] state[populated=275856] buckets[few=6, many=275769, some=81] sources[none] quality[none]
- funding_rate: presence[absent=16033, present=259823] state[empty=16033, populated=259823] buckets[few=259823, none=16033] sources[none] quality[none]
- liquidation_clusters: presence[absent=140195, present=135661] state[empty=140195, populated=135661] buckets[few=110576, none=140195, some=25085] sources[none] quality[none]
- oi_snapshot: presence[absent=16032, present=259824] state[empty=16032, populated=259824] buckets[few=242, many=257902, none=16032, some=1680] sources[none] quality[none]
- order_book: presence[absent=72463, present=203393] state[populated=203393, unavailable=72463] buckets[few=203393, none=72463] sources[book_ticker=203393, unavailable=72463] quality[none=72463, top_of_book_only=203393]
- orderblocks: presence[absent=275856] state[empty=275856] buckets[none=275856] sources[not_implemented=275856] quality[none]
- recent_ticks: presence[absent=7602, present=268254] state[empty=7602, populated=268254] buckets[many=268254, none=7602] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.3238041400909424` sec
- Median create→first breach: `10952.249774932861` sec
- Median create→terminal: `11053.017921924591` sec
- Median first breach→terminal: `1.2875261306762695` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.2527 | 2070.325546979904 | 2071.6130731105804 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.7195 | 19756.710076093674 | 19757.962670087814 |
| MOVER_TREND_PULLBACK | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.0373 | 11590.330823540688 | 11641.298041939735 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9041 | 8877.235203027725 | 8879.41350889206 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 12696 | 10 | 10110 | 0.0 | 0.0 | None | None | 2586 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1273 | 1 | 1219 | 0.0 | 100.0 | 8877.235203027725 | 8879.41350889206 | 54 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-155`
- Gating Δ: `-44552`
- No-generation Δ: `-857030`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.6775, "current_avg_pnl": -2.2527, "current_win_rate": 0.0, "previous_avg_pnl": -0.5752, "previous_win_rate": 25.0, "win_rate_delta": -25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -26, "geometry_changed_delta": 0, "geometry_preserved_delta": -1922, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 24, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 8877.24, "median_terminal_delta_sec": 8879.41, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::WHALE_MOMENTUM**
- Most promising healthy path: **none**
- Most likely bottleneck: **MOVER_AVWAP_SCALP**
- Suggested next investigation target: **EVAL::WHALE_MOMENTUM**
