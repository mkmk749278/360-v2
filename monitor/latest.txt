# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `14613` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 122 | 122 | 122 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11286 | 11286 | 10578 | 4 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 78116 | 78126 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 65064 | 65075 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 64804 | 61253 | 3806 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 65096 | 62023 | 3215 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 75344 | 75152 | 215 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 65075 | 65085 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 65246 | 65280 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 84111 | 85912 | 1290 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 78132 | 70454 | 13628 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 73354 | 73360 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 65083 | 65085 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 64748 | 64234 | 561 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 62736 | 61041 | 3667 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 54381 | 51555 | 3007 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 54563 | 54229 | 372 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 78086 | 78035 | 81 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 65092 | 65097 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 10236 | 10236 | 8395 | 16 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 585 | 585 | 532 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14616 | 14616 | 14601 | 1 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 7 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3497 | 3497 | 3494 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 28480 | 28480 | 26001 | 13 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 19 | 19 | 19 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2406 | 2406 | 2031 | 14 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 12361 | 12361 | 10034 | 16 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1811 | 1811 | 1798 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 178 | 178 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=78126): breakout_not_found=38116, basic_filters_failed=21190, move_not_fresh=14495, breakout_stale=2926, retest_proximity_failed=740, insufficient_candles=497, volume_spike_missing=155, ema_alignment_reject=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=65075): cls_disabled_merged_into_lsr=65075
- **EVAL::DIVERGENCE_CONTINUATION** (total=61253): cvd_divergence_failed=21648, h1_trend_not_aligned=17089, basic_filters_failed=14689, ema_alignment_reject=6420, retest_proximity_failed=845, missing_fvg_or_orderblock=562
- **EVAL::FAILED_AUCTION_RECLAIM** (total=62023): auction_not_detected=25292, basic_filters_failed=14663, reclaim_hold_failed=12644, tail_too_small=8863, regime_blocked=561
- **EVAL::FUNDING_EXTREME** (total=75152): funding_not_extreme=55188, basic_filters_failed=16559, ema_alignment_reject=1740, missing_funding_rate=908, rsi_reject=376, cvd_divergence_failed=210, momentum_reject=121, missing_fvg_or_orderblock=28, insufficient_candles=22
- **EVAL::LIQUIDATION_REVERSAL** (total=65085): cascade_threshold_not_met=47941, basic_filters_failed=16416, insufficient_candles=277, cvd_divergence_failed=260, rsi_reject=177, volume_spike_missing=12, missing_fvg_or_orderblock=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=65280): no_ma_cross=49849, basic_filters_failed=14698, ma_cross_cooldown=545, ma_cross_htf_misaligned=188
- **EVAL::MOVER_AVWAP_SCALP** (total=85912): no_mover_leg=29483, no_avwap_tag=26575, basic_filters_failed=20829, avwap_slope_against=6494, insufficient_candles=2346, no_avwap_reclaim=102, avwap_reclaim_no_volume=83
- **EVAL::MOVER_TREND_PULLBACK** (total=70454): mover_run_too_small=37300, basic_filters_failed=20782, no_reclaim=8298, insufficient_candles=2346, no_pullback_tag=1728
- **EVAL::OPENING_RANGE_BREAKOUT** (total=73360): feature_disabled=73360
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=65085): regime_blocked=44573, breakout_not_found=13887, basic_filters_failed=4941, adx_reject=1658, ema_alignment_reject=24, rsi_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=64234): regime_blocked=21031, compression_not_detected=18733, breakout_not_detected=12347, basic_filters_failed=9715, volume_confirmation_failed=2035, rsi_reject=318, missing_fvg_or_orderblock=55
- **EVAL::SR_FLIP_RETEST** (total=61041): basic_filters_failed=14646, flip_close_not_confirmed=12384, long_break_volume_thin=7999, retest_out_of_zone=7945, whipsaw_flip=6419, reclaim_hold_failed=4864, long_disabled=4090, wick_quality_failed=1078, long_acceptance_not_held=671, regime_blocked=561, missing_fvg_or_orderblock=157, ema_alignment_reject=117, rsi_reject=110
- **EVAL::STANDARD** (total=51555): momentum_reject=19576, sweeps_not_detected=9356, adx_reject=7524, macd_reject=6320, basic_filters_failed=4983, ema_alignment_reject=2563, rsi_reject=1008, invalid_sl_geometry=225
- **EVAL::TREND_PULLBACK** (total=54229): h1_trend_not_aligned=20100, ema_alignment_reject=7592, basic_filters_failed=6798, h1_pullback_not_confirmed=6137, no_ema_reclaim_close=3700, ema_not_tested_prev=3013, body_conviction_fail=2871, rsi_reject=2557, prev_already_above_emas=596, prev_already_below_emas=248, no_prev_low_break=211, no_prev_high_break=188, momentum_flat=95, missing_fvg_or_orderblock=81, momentum_reject=30, ema21_not_tagged=12
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=78035): breakout_not_found=45826, basic_filters_failed=21189, move_not_fresh=7108, breakout_stale=2741, retest_proximity_failed=563, insufficient_candles=497, volume_spike_missing=100, ema_alignment_reject=11
- **EVAL::WHALE_MOMENTUM** (total=65097): momentum_reject=45153, recent_ticks_insufficient=14178, basic_filters_failed=5766

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 160661 | 41.8% |
| QUIET | 106742 | 27.8% |
| TRENDING_DOWN | 72466 | 18.9% |
| TRENDING_UP | 38171 | 9.9% |
| VOLATILE | 6020 | 1.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **190**
- Average confidence gap to threshold: **11.55** (samples=190) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BCHUSDT=31, BTCUSDT=29, TRXUSDT=24, BZUSDT=21, LINKUSDT=15, AVAXUSDT=14, ONDOUSDT=12, XRPUSDT=11, DOGEUSDT=10, SOXLUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 43 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 9 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 45 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 315 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 30 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 144 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 3 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 220 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1677 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 114 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 60 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 57 |
| SR_FLIP_RETEST | filtered | min_confidence | 159 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 37 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 146 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 2 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 11 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 130 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 52 | 52.36 | 65.00 | 12.64 | 21.02 | 19.84 | 17.57 | 0.88 | 16.80 |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.43 | 65.00 | -3.43 | 20.89 | 19.74 | 18.21 | 1.51 | 3.80 |
| FAILED_AUCTION_RECLAIM | filtered | 345 | 51.75 | 65.00 | 13.25 | 19.74 | 19.42 | 20.00 | 4.61 | 5.99 |
| FAILED_AUCTION_RECLAIM | kept | 144 | 70.43 | 65.00 | -5.43 | 21.92 | 19.59 | 20.00 | 4.22 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 45.50 | 65.00 | 19.50 | 20.14 | 20.00 | 17.26 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 58.50 | 65.00 | 6.50 | 21.20 | 17.20 | 17.00 | 5.00 | 17.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 72.70 | 65.00 | -7.70 | 21.20 | 19.20 | 17.00 | 5.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 3 | 79.27 | 65.00 | -14.27 | 17.40 | 16.77 | 15.80 | 4.67 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 220 | 55.63 | 65.00 | 9.37 | 20.94 | 18.10 | 15.80 | 4.71 | 11.47 |
| MOVER_TREND_PULLBACK | kept | 1677 | 78.13 | 65.00 | -13.13 | 20.05 | 18.52 | 15.80 | 4.48 | 1.56 |
| QUIET_COMPRESSION_BREAK | filtered | 174 | 58.57 | 65.00 | 6.43 | 20.87 | 19.92 | 20.00 | 0.00 | 11.49 |
| QUIET_COMPRESSION_BREAK | kept | 57 | 72.65 | 65.00 | -7.65 | 22.21 | 19.47 | 20.00 | 0.00 | 3.05 |
| SR_FLIP_RETEST | filtered | 196 | 53.75 | 65.00 | 11.25 | 20.73 | 19.81 | 16.14 | 1.68 | 14.91 |
| SR_FLIP_RETEST | kept | 146 | 71.84 | 65.00 | -6.84 | 20.24 | 19.78 | 16.12 | 1.91 | 1.01 |
| TREND_PULLBACK_EMA | filtered | 2 | 57.50 | 65.00 | 7.50 | 20.00 | 19.70 | 18.80 | 4.00 | 17.00 |
| TREND_PULLBACK_EMA | kept | 11 | 87.36 | 65.00 | -22.36 | 21.42 | 20.00 | 15.65 | 5.50 | -2.73 |
| VOLUME_SURGE_BREAKOUT | filtered | 130 | 52.70 | 65.00 | 12.30 | 19.63 | 18.85 | 20.00 | 3.89 | 10.64 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 52 | 52.36 | 20.69 | 12.62 | 7.56 | 13.69 | 5.11 | 8.59 | 0.88 |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.43 | 22.51 | 14.44 | 8.80 | 11.67 | 5.07 | 8.83 | 1.51 |
| FAILED_AUCTION_RECLAIM | filtered | 345 | 51.75 | 21.70 | 17.43 | 4.79 | 12.49 | 6.32 | 4.44 | 4.61 |
| FAILED_AUCTION_RECLAIM | kept | 144 | 70.43 | 21.78 | 14.69 | 3.10 | 11.63 | 7.79 | 7.22 | 4.22 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 45.50 | 25.00 | 8.00 | 8.14 | 17.00 | 5.71 | 1.64 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 58.50 | 25.00 | 14.00 | 6.00 | 9.00 | 8.00 | 8.70 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 72.70 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 8.70 | 5.00 |
| MOVER_AVWAP_SCALP | kept | 3 | 79.27 | 19.67 | 18.00 | 10.50 | 12.00 | 5.00 | 9.43 | 4.67 |
| MOVER_TREND_PULLBACK | filtered | 220 | 55.63 | 17.37 | 18.00 | 8.22 | 14.60 | 5.35 | 8.88 | 4.71 |
| MOVER_TREND_PULLBACK | kept | 1677 | 78.13 | 19.59 | 18.00 | 8.03 | 14.34 | 5.86 | 9.40 | 4.48 |
| QUIET_COMPRESSION_BREAK | filtered | 174 | 58.57 | 17.37 | 16.62 | 13.26 | 14.21 | 7.30 | 3.12 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 57 | 72.65 | 17.42 | 17.86 | 11.68 | 14.16 | 7.47 | 7.09 | 0.00 |
| SR_FLIP_RETEST | filtered | 196 | 53.75 | 20.21 | 16.11 | 6.46 | 14.73 | 5.55 | 3.91 | 1.68 |
| SR_FLIP_RETEST | kept | 146 | 71.84 | 21.67 | 18.00 | 6.21 | 11.24 | 5.38 | 8.98 | 1.91 |
| TREND_PULLBACK_EMA | filtered | 2 | 57.50 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 4.00 |
| TREND_PULLBACK_EMA | kept | 11 | 87.36 | 24.27 | 18.00 | 7.50 | 14.00 | 8.18 | 9.91 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 130 | 52.70 | 15.53 | 15.66 | 12.67 | 14.00 | 5.00 | 5.36 | 3.89 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 52 | 52.36 | 0.00 | 0.00 | 0.15 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.95** |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 345 | 51.75 | 0.00 | 0.00 | 3.08 | 0.00 | 1.76 | 0.00 | 0.00 | 0.00 | **4.84** |
| FAILED_AUCTION_RECLAIM | kept | 144 | 70.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 45.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 58.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 72.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 3 | 79.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 220 | 55.63 | 0.00 | 0.00 | 5.96 | 0.00 | 1.69 | 0.00 | 0.00 | 0.00 | **7.65** |
| MOVER_TREND_PULLBACK | kept | 1677 | 78.13 | 0.00 | 0.00 | 0.55 | 0.00 | 0.98 | 0.00 | 0.00 | 0.00 | **1.53** |
| QUIET_COMPRESSION_BREAK | filtered | 174 | 58.57 | 0.00 | 0.00 | 0.00 | 0.00 | 1.16 | 0.00 | 0.00 | 7.47 | **8.63** |
| QUIET_COMPRESSION_BREAK | kept | 57 | 72.65 | 0.00 | 0.00 | 0.00 | 0.00 | 2.91 | 0.00 | 0.00 | 0.29 | **3.20** |
| SR_FLIP_RETEST | filtered | 196 | 53.75 | 0.00 | 0.00 | 0.00 | 0.00 | 3.31 | 0.00 | 0.00 | 4.82 | **8.13** |
| SR_FLIP_RETEST | kept | 146 | 71.84 | 0.00 | 0.00 | 0.03 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | **0.33** |
| TREND_PULLBACK_EMA | filtered | 2 | 57.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 11 | 87.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 130 | 52.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=34 (68.0%) | PREMATURE=9 (18.0%) | NEUTRAL=7 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 25 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 34 | 9 | 7 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 0 | 3 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 3 | 5 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 9 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 14 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 5 | 2 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 34 | 9 | 7 | 27.1 | 10.0 | +0.34 | **KEEP** — net-helping: avg +0.34R/kill across 50 kills (saved 27.1R vs missed 10.0R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `81238`
- `Path funnel` emissions: `47`
- `Regime distribution` emissions: `47`
- `QUIET_SCALP_BLOCK` events: `190`
- `confidence_gate` events: `3212`
- `free_channel_post` events: `3`
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
| futures_liq | 9 | 2478 | 3060 | 3153 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[present=298408] state[populated=298408] buckets[few=6, many=298321, some=81] sources[none] quality[none]
- funding_rate: presence[absent=29544, present=268864] state[empty=29544, populated=268864] buckets[few=268864, none=29544] sources[none] quality[none]
- liquidation_clusters: presence[absent=168606, present=129802] state[empty=168606, populated=129802] buckets[few=108518, none=168606, some=21284] sources[none] quality[none]
- oi_snapshot: presence[absent=29543, present=268865] state[empty=29543, populated=268865] buckets[few=242, many=266943, none=29543, some=1680] sources[none] quality[none]
- order_book: presence[absent=78002, present=220406] state[populated=220406, unavailable=78002] buckets[few=220406, none=78002] sources[book_ticker=220406, unavailable=78002] quality[none=78002, top_of_book_only=220406]
- orderblocks: presence[absent=298408] state[empty=298408] buckets[none=298408] sources[not_implemented=298408] quality[none]
- recent_ticks: presence[absent=5071, present=293337] state[empty=5071, populated=293337] buckets[many=293337, none=5071] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.3880789279937744` sec
- Median create→first breach: `8672.074809789658` sec
- Median create→terminal: `8675.000941991806` sec
- Median first breach→terminal: `2.2338759899139404` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1824 | 1368.5721039772034 | 1370.5175740718842 |
| FAILED_AUCTION_RECLAIM | 9 | 9 | 22.2 | 77.8 | 22.2 | 0.0 | -0.7805 | 6634.841500043869 | 6638.684967041016 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.7195 | 19756.710076093674 | 19757.962670087814 |
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 60.0 | 0.0 | 0.0 | -0.2051 | 10952.249774932861 | 11053.017921924591 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9041 | 8877.235203027725 | 8879.41350889206 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.0818 | 2421.717633962631 | 2423.659257888794 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 12361 | 16 | 10034 | 0.0 | 0.0 | None | None | 2327 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1811 | 1 | 1798 | 0.0 | 100.0 | 8877.235203027725 | 8879.41350889206 | 13 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `66`
- Gating Δ: `77612`
- No-generation Δ: `1140996`
- Fast failures Δ: `-1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.4438, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.4438, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -1.669, "current_avg_pnl": -1.1824, "current_win_rate": 0.0, "previous_avg_pnl": 0.4866, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.3186, "current_avg_pnl": -0.7805, "current_win_rate": 22.2, "previous_avg_pnl": 0.5381, "previous_win_rate": 9.5, "win_rate_delta": 12.7}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -2.1274, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 2.1274, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.6359, "current_avg_pnl": -1.7195, "current_win_rate": 0.0, "previous_avg_pnl": -0.0836, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.2592, "current_avg_pnl": -0.2051, "current_win_rate": 0.0, "previous_avg_pnl": -0.4643, "previous_win_rate": 5.6, "win_rate_delta": -5.6}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.4608, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.4608, "previous_win_rate": 40.0, "win_rate_delta": -40.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 16, "geometry_changed_delta": 0, "geometry_preserved_delta": 2327, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1167.68, "median_terminal_delta_sec": -1446.89, "sl_rate_delta": -25.0, "win_rate_delta": -40.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 13, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 8877.24, "median_terminal_delta_sec": 8879.41, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
