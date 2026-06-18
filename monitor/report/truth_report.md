# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `9` sec (warning=False)
- Latest performance record age: `1899` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 7797 | 7797 | 7383 | 10 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 40245 | 40245 | 36313 | 29 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 167342 | 166038 | 1466 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 158751 | 158760 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 157826 | 148409 | 10330 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 158808 | 152552 | 6645 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 171385 | 171252 | 170 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 167102 | 167112 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 159203 | 159243 | 15 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 167503 | 167511 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 158769 | 158790 | 13 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 157781 | 157310 | 514 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 153873 | 145104 | 12628 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 152689 | 142185 | 11222 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 153414 | 152526 | 958 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 167268 | 166975 | 366 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 167121 | 166874 | 388 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 26139 | 26139 | 21294 | 48 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1052 | 1052 | 1035 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 34 | 34 | 34 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 55332 | 55332 | 49635 | 80 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 22 | 22 | 20 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1975 | 1975 | 1825 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 53028 | 53028 | 36739 | 95 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3799 | 3799 | 3756 | 8 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2003 | 2003 | 1048 | 7 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 11328 | 11328 | 9052 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=166038): breakout_not_found=72747, basic_filters_failed=57047, retest_proximity_failed=29463, volume_spike_missing=4776, ema_alignment_reject=928, insufficient_candles=581, missing_fvg_or_orderblock=496
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=158760): cls_disabled_merged_into_lsr=158760
- **EVAL::DIVERGENCE_CONTINUATION** (total=148409): basic_filters_failed=50379, cvd_divergence_failed=47417, h1_trend_not_aligned=30102, ema_alignment_reject=11036, regime_blocked=4904, retest_proximity_failed=2908, missing_fvg_or_orderblock=892, insufficient_candles=466, cvd_insufficient=303, missing_cvd=2
- **EVAL::FAILED_AUCTION_RECLAIM** (total=152552): auction_not_detected=53513, basic_filters_failed=48321, reclaim_hold_failed=24186, tail_too_small=18777, regime_blocked=7288, insufficient_candles=466, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=171252): funding_not_extreme=109399, basic_filters_failed=54167, missing_funding_rate=5898, ema_alignment_reject=928, rsi_reject=550, insufficient_candles=116, cvd_divergence_failed=112, momentum_reject=51, missing_fvg_or_orderblock=31
- **EVAL::LIQUIDATION_REVERSAL** (total=167112): cascade_threshold_not_met=106463, basic_filters_failed=57045, rsi_reject=1488, cvd_divergence_failed=1429, insufficient_candles=555, missing_fvg_or_orderblock=88, volume_spike_missing=39, cvd_insufficient=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=159243): no_ma_cross=106393, basic_filters_failed=50398, ma_cross_cooldown=1782, ma_cross_htf_misaligned=531, ma_cross_htf_unconfirmed=139
- **EVAL::OPENING_RANGE_BREAKOUT** (total=167511): feature_disabled=167511
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=158790): regime_blocked=105511, breakout_not_found=28969, basic_filters_failed=20976, adx_reject=3304, ema_alignment_reject=30
- **EVAL::QUIET_COMPRESSION_BREAK** (total=157310): regime_blocked=60198, compression_not_detected=53151, basic_filters_failed=27335, breakout_not_detected=14101, macd_reject=897, volume_confirmation_failed=852, insufficient_candles=522, rsi_reject=246, missing_fvg_or_orderblock=8
- **EVAL::SR_FLIP_RETEST** (total=145104): basic_filters_failed=48131, retest_out_of_zone=31074, reclaim_hold_failed=28005, flip_close_not_confirmed=21461, regime_blocked=7235, wick_quality_failed=4768, ema_alignment_reject=2695, missing_fvg_or_orderblock=866, insufficient_candles=831, rsi_reject=38
- **EVAL::STANDARD** (total=142185): adx_reject=34959, momentum_reject=31511, basic_filters_failed=28615, sweeps_not_detected=23438, macd_reject=12741, ema_alignment_reject=8313, invalid_sl_geometry=1285, insufficient_candles=665, rsi_reject=636, mtf_reject=22
- **EVAL::TREND_PULLBACK** (total=152526): h1_trend_not_aligned=40698, basic_filters_failed=28292, ema_alignment_reject=21354, h1_pullback_not_confirmed=15843, ema_not_tested_prev=13010, regime_blocked=11068, no_ema_reclaim_close=9165, body_conviction_fail=4947, rsi_reject=3939, prev_already_below_emas=1401, no_prev_low_break=697, prev_already_above_emas=695, insufficient_candles=665, no_prev_high_break=346, momentum_flat=233, ema21_not_tagged=104, missing_fvg_or_orderblock=48, momentum_reject=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=166975): breakout_not_found=89376, basic_filters_failed=57046, retest_proximity_failed=15044, volume_spike_missing=3584, ema_alignment_reject=1072, insufficient_candles=581, missing_fvg_or_orderblock=268, rsi_reject=4
- **EVAL::WHALE_MOMENTUM** (total=166874): momentum_reject=123820, recent_ticks_insufficient=27891, basic_filters_failed=15163

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 345252 | 38.0% |
| QUIET | 207596 | 22.8% |
| TRENDING_DOWN | 180248 | 19.8% |
| TRENDING_UP | 98182 | 10.8% |
| VOLATILE | 78124 | 8.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **513**
- Average confidence gap to threshold: **15.83** (samples=513) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: MRVLUSDT=60, LITEUSDT=56, LINKUSDT=43, LTCUSDT=36, ETHUSDT=35, SNDKUSDT=35, TRXUSDT=33, BTCUSDT=31, 1000PEPEUSDT=31, AAVEUSDT=30

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 72 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 158 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 297 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 942 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 153 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 881 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1049 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 102 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1025 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 32 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 135 |
| SR_FLIP_RETEST | filtered | min_confidence | 4209 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 198 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1212 |
| TREND_PULLBACK_CONTINUATION | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 27 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 299 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 11 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 207 |
| WHALE_MOMENTUM | filtered | min_confidence | 357 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 14 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 29 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 72 | 69.76 | 65.00 | -4.76 | 20.72 | 19.69 | 19.97 | 0.00 | 2.72 |
| DIVERGENCE_CONTINUATION | filtered | 161 | 55.04 | 65.00 | 9.96 | 20.30 | 19.86 | 18.07 | 1.58 | 6.91 |
| DIVERGENCE_CONTINUATION | kept | 297 | 68.88 | 65.00 | -3.88 | 20.40 | 19.20 | 17.92 | 1.84 | -1.34 |
| FAILED_AUCTION_RECLAIM | filtered | 1095 | 54.07 | 65.00 | 10.93 | 21.04 | 18.83 | 20.00 | 3.88 | 2.99 |
| FAILED_AUCTION_RECLAIM | kept | 881 | 72.69 | 65.00 | -7.69 | 21.63 | 19.07 | 20.00 | 4.29 | 0.23 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 45.00 | 65.00 | 20.00 | 20.60 | 20.00 | 17.00 | 2.00 | 17.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1151 | 52.81 | 65.00 | 12.19 | 20.73 | 19.63 | 18.02 | 2.57 | 5.63 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1025 | 69.56 | 65.00 | -4.56 | 21.19 | 19.59 | 18.10 | 1.89 | 0.52 |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 53.64 | 65.00 | 11.36 | 21.53 | 20.00 | 20.00 | 0.00 | 4.97 |
| QUIET_COMPRESSION_BREAK | kept | 135 | 72.56 | 65.00 | -7.56 | 21.14 | 19.89 | 20.00 | 0.00 | -0.29 |
| SR_FLIP_RETEST | filtered | 4407 | 54.12 | 65.00 | 10.88 | 21.40 | 19.88 | 15.96 | 1.93 | 3.60 |
| SR_FLIP_RETEST | kept | 1212 | 71.19 | 65.00 | -6.19 | 21.30 | 19.95 | 16.11 | 1.98 | -0.65 |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 65.00 | 65.00 | 0.00 | 21.00 | 15.80 | 16.40 | 0.00 | 0.00 |
| TREND_PULLBACK_EMA | kept | 27 | 79.67 | 65.00 | -14.67 | 21.61 | 19.44 | 17.31 | 5.89 | -0.67 |
| VOLUME_SURGE_BREAKOUT | filtered | 310 | 51.48 | 65.00 | 13.52 | 20.10 | 19.83 | 19.98 | 1.32 | 4.64 |
| VOLUME_SURGE_BREAKOUT | kept | 207 | 73.53 | 65.00 | -8.53 | 20.62 | 19.97 | 19.96 | 1.72 | 3.14 |
| WHALE_MOMENTUM | filtered | 371 | 59.19 | 65.00 | 5.81 | 23.70 | 19.35 | 17.00 | 0.00 | 10.07 |
| WHALE_MOMENTUM | kept | 29 | 68.14 | 65.00 | -3.14 | 23.24 | 19.90 | 17.00 | 0.00 | 10.17 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 72 | 69.76 | 22.00 | 15.69 | 12.83 | 11.72 | 5.01 | 5.22 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 161 | 55.04 | 23.56 | 10.55 | 6.54 | 12.34 | 5.53 | 7.84 | 1.58 |
| DIVERGENCE_CONTINUATION | kept | 297 | 68.88 | 21.85 | 14.77 | 4.25 | 12.99 | 5.77 | 7.68 | 1.84 |
| FAILED_AUCTION_RECLAIM | filtered | 1095 | 54.07 | 22.30 | 16.83 | 5.26 | 12.01 | 6.13 | 4.53 | 3.88 |
| FAILED_AUCTION_RECLAIM | kept | 881 | 72.69 | 22.55 | 15.97 | 4.67 | 12.12 | 6.81 | 6.56 | 4.29 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 45.00 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1151 | 52.81 | 21.78 | 14.38 | 6.82 | 12.42 | 5.85 | 5.05 | 2.57 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1025 | 69.56 | 22.41 | 14.31 | 5.36 | 13.44 | 5.77 | 6.89 | 1.89 |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 53.64 | 17.25 | 18.00 | 9.94 | 14.00 | 6.97 | 2.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 135 | 72.56 | 19.13 | 15.33 | 9.02 | 13.96 | 8.50 | 7.18 | 0.00 |
| SR_FLIP_RETEST | filtered | 4407 | 54.12 | 21.15 | 17.55 | 5.00 | 13.92 | 6.02 | 5.68 | 1.93 |
| SR_FLIP_RETEST | kept | 1212 | 71.19 | 21.25 | 16.97 | 4.78 | 13.98 | 6.00 | 7.33 | 1.98 |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 65.00 | 17.00 | 8.00 | 9.00 | 11.00 | 10.00 | 10.00 | 0.00 |
| TREND_PULLBACK_EMA | kept | 27 | 79.67 | 19.07 | 18.00 | 7.11 | 14.22 | 6.56 | 8.89 | 5.89 |
| VOLUME_SURGE_BREAKOUT | filtered | 310 | 51.48 | 19.43 | 14.94 | 10.99 | 13.77 | 5.48 | 5.04 | 1.32 |
| VOLUME_SURGE_BREAKOUT | kept | 207 | 73.53 | 20.40 | 14.39 | 13.16 | 13.38 | 6.43 | 7.33 | 1.72 |
| WHALE_MOMENTUM | filtered | 371 | 59.19 | 20.39 | 16.11 | 8.01 | 12.62 | 6.32 | 5.81 | 0.00 |
| WHALE_MOMENTUM | kept | 29 | 68.14 | 24.72 | 18.00 | 9.83 | 13.62 | 5.41 | 6.72 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 72 | 69.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 161 | 55.04 | 0.00 | 0.00 | 2.77 | 0.00 | 3.46 | 0.00 | 0.00 | 0.00 | **6.23** |
| DIVERGENCE_CONTINUATION | kept | 297 | 68.88 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.03** |
| FAILED_AUCTION_RECLAIM | filtered | 1095 | 54.07 | 0.00 | 0.00 | 0.62 | 0.00 | 1.25 | 0.00 | 0.00 | 0.00 | **1.87** |
| FAILED_AUCTION_RECLAIM | kept | 881 | 72.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.01** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 45.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1151 | 52.81 | 0.00 | 0.00 | 1.38 | 0.00 | 4.05 | 0.00 | 0.00 | 0.00 | **5.43** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1025 | 69.56 | 0.00 | 0.00 | 0.11 | 0.00 | 0.34 | 0.00 | 0.00 | 0.00 | **0.45** |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 53.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.94 | 0.00 | 0.00 | 0.00 | **0.94** |
| QUIET_COMPRESSION_BREAK | kept | 135 | 72.56 | 0.00 | 0.00 | 0.00 | 0.00 | 1.85 | 0.00 | 0.00 | 0.00 | **1.85** |
| SR_FLIP_RETEST | filtered | 4407 | 54.12 | 0.00 | 0.00 | 1.12 | 0.00 | 1.06 | 0.00 | 0.00 | 0.47 | **2.65** |
| SR_FLIP_RETEST | kept | 1212 | 71.19 | 0.00 | 0.00 | 0.01 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | **0.31** |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 27 | 79.67 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.18** |
| VOLUME_SURGE_BREAKOUT | filtered | 310 | 51.48 | 0.00 | 0.00 | 0.95 | 0.00 | 0.97 | 0.00 | 0.00 | 0.00 | **1.92** |
| VOLUME_SURGE_BREAKOUT | kept | 207 | 73.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| WHALE_MOMENTUM | filtered | 371 | 59.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | kept | 29 | 68.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=89 (76.1%) | PREMATURE=16 (13.7%) | NEUTRAL=12 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 73 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 27 | 3 | 0 | 0 |
| ema_crossover | 2 | 1 | 1 | 0 |
| momentum_loss | 51 | 7 | 5 | 0 |
| trailing_invalidation | 9 | 5 | 6 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 0 | 4 | 0 |
| DIVERGENCE_CONTINUATION | 15 | 4 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 16 | 2 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 18 | 2 | 4 | 0 |
| SR_FLIP_RETEST | 34 | 8 | 3 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 27 | 3 | 0 | 9.3 | 5.6 | +0.13 | **KEEP** — net-helping: avg +0.13R/kill across 30 kills (saved 9.3R vs missed 5.6R) |
| ema_crossover | 2 | 1 | 1 | 1.1 | 2.0 | -0.21 | **INSUFFICIENT_SAMPLE** — only 4 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 51 | 7 | 5 | 34.1 | 11.3 | +0.36 | **KEEP** — net-helping: avg +0.36R/kill across 63 kills (saved 34.1R vs missed 11.3R) |
| trailing_invalidation | 9 | 5 | 6 | 8.9 | 7.2 | +0.09 | **TUNE** — marginal: avg +0.09R/kill across 20 kills — consider per-setup exemption or threshold adjustment, not full drop |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4050776`
- `Path funnel` emissions: `128`
- `Regime distribution` emissions: `128`
- `QUIET_SCALP_BLOCK` events: `513`
- `confidence_gate` events: `11414`
- `free_channel_post` events: `96`
- `pre_tp_fire` events: `45`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **45**
- Avg resolved threshold: **0.504%** raw → avg net **+4.34%** @ 10x
- Avg time-to-fire from dispatch: **229s**
- By threshold source: stamped=45

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 18 | 0.489% | +4.19% | 302 | stamped=18 |
| FAILED_AUCTION_RECLAIM | 9 | 0.358% | +2.88% | 104 | stamped=9 |
| LIQUIDITY_SWEEP_REVERSAL | 9 | 0.515% | +4.45% | 234 | stamped=9 |
| DIVERGENCE_CONTINUATION | 6 | 0.427% | +3.57% | 115 | stamped=6 |
| TREND_PULLBACK_EMA | 2 | 0.779% | +7.09% | 497 | stamped=2 |
| TREND_PULLBACK_CONTINUATION | 1 | 1.926% | +18.56% | 125 | stamped=1 |
- Top symbols: XPLUSDT=7, AEROUSDT=6, SNDKUSDT=4, EVAAUSDT=4, STGUSDT=3, TIAUSDT=3, PORTALUSDT=3, BRUSDT=2, LITEUSDT=2, TACUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 1713 | 1713 | 1713 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **96**

| Source | Count |
|---|---:|
| signal_close | 47 |
| pre_tp | 45 |
| regime_shift | 4 |

- By severity: HIGH=96

## Dependency readiness
- cvd: presence[absent=12, present=739407] state[empty=12, populated=739407] buckets[few=896, many=723595, none=12, some=14916] sources[none] quality[none]
- funding_rate: presence[absent=13718, present=725701] state[empty=13718, populated=725701] buckets[few=725701, none=13718] sources[none] quality[none]
- liquidation_clusters: presence[absent=347379, present=392040] state[empty=347379, populated=392040] buckets[few=301734, none=347379, some=90306] sources[none] quality[none]
- oi_snapshot: presence[absent=6373, present=733046] state[empty=6373, populated=733046] buckets[few=394, many=732268, none=6373, some=384] sources[none] quality[none]
- order_book: presence[absent=195707, present=543712] state[populated=543712, unavailable=195707] buckets[few=543712, none=195707] sources[book_ticker=543712, unavailable=195707] quality[none=195707, top_of_book_only=543712]
- orderblocks: presence[absent=739419] state[empty=739419] buckets[none=739419] sources[not_implemented=739419] quality[none]
- recent_ticks: presence[absent=40168, present=699251] state[empty=40168, populated=699251] buckets[many=699251, none=40168] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.340033411979675` sec
- Median create→first breach: `405.3540849685669` sec
- Median create→terminal: `368.1716299057007` sec
- Median first breach→terminal: `1.2191030979156494` sec
- Fast-failure buckets: `{"under_120s": {"count": 12, "pct": 25.5}, "under_180s": {"count": 14, "pct": 29.8}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 7, "pct": 14.9}}`
- ~3 minute terminal-close behavior: `{"count": 10, "pct": 13.2}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | -0.2219 | None | 528.66588139534 |
| DIVERGENCE_CONTINUATION | 11 | 11 | 0.0 | 9.1 | 0.0 | 54.5 | 0.0386 | 224.79163193702698 | 129.9092309474945 |
| FAILED_AUCTION_RECLAIM | 15 | 15 | 0.0 | 0.0 | 0.0 | 60.0 | 0.0159 | 177.10217952728271 | 292.19445395469666 |
| LIQUIDITY_SWEEP_REVERSAL | 18 | 18 | 0.0 | 5.6 | 0.0 | 50.0 | -0.0048 | 694.2599874734879 | 359.019029378891 |
| SR_FLIP_RETEST | 24 | 24 | 0.0 | 16.7 | 0.0 | 75.0 | 0.0301 | 405.3540849685669 | 436.5209490060806 |
| TREND_PULLBACK_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 100.0 | 0.9632 | 604.4319219589233 | 604.9377450942993 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 100.0 | -0.2244 | 651.7244169712067 | 525.0155099630356 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9586 | 577.1213998794556 | 611.2133808135986 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 53028 | 95 | 36739 | 0.0 | 16.7 | 405.3540849685669 | 436.5209490060806 | 16289 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3799 | 8 | 3756 | 0.0 | 0.0 | 651.7244169712067 | 525.0155099630356 | 43 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-199`
- Gating Δ: `26131`
- No-generation Δ: `-151305`
- Fast failures Δ: `3`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.5489, "current_avg_pnl": -0.2219, "current_win_rate": 0.0, "previous_avg_pnl": 0.327, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0417, "current_avg_pnl": 0.0386, "current_win_rate": 0.0, "previous_avg_pnl": 0.0803, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1155, "current_avg_pnl": 0.0159, "current_win_rate": 0.0, "previous_avg_pnl": -0.0996, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.05, "current_avg_pnl": -0.0048, "current_win_rate": 0.0, "previous_avg_pnl": -0.0548, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0185, "current_avg_pnl": 0.0301, "current_win_rate": 0.0, "previous_avg_pnl": 0.0116, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -121, "geometry_changed_delta": 0, "geometry_preserved_delta": -11503, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 44.4, "median_terminal_delta_sec": 84.87, "sl_rate_delta": 7.8, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -298, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -713.22, "median_terminal_delta_sec": -605.57, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
