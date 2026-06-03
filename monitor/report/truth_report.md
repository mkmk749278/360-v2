# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `54` sec (warning=False)
- Latest performance record age: `750` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 634 | 634 | 139 | 12 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5559 | 5559 | 4246 | 87 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 28747 | 28544 | 218 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 25838 | 25841 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 25736 | 23873 | 1964 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 25849 | 24560 | 1326 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 28935 | 28851 | 90 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 28728 | 28727 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 25888 | 25896 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 28764 | 28768 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 25842 | 25841 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 25735 | 25736 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 25561 | 23672 | 2054 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 25427 | 23177 | 2323 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 25502 | 25281 | 240 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 28738 | 28677 | 70 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 28731 | 28728 | 9 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3606 | 3606 | 3016 | 56 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 259 | 259 | 202 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 16 | 16 | 16 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 6298 | 6298 | 5502 | 120 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 12 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 5594 | 5594 | 2399 | 288 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 748 | 748 | 642 | 18 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 204 | 204 | 91 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 99 | 99 | 99 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=28544): breakout_not_found=18651, retest_proximity_failed=5867, basic_filters_failed=2504, volume_spike_missing=1144, ema_alignment_reject=310, missing_fvg_or_orderblock=68
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=25841): cls_disabled_merged_into_lsr=25841
- **EVAL::DIVERGENCE_CONTINUATION** (total=23873): cvd_divergence_failed=12871, h1_trend_not_aligned=4023, ema_alignment_reject=3474, basic_filters_failed=2304, retest_proximity_failed=885, regime_blocked=165, missing_fvg_or_orderblock=151
- **EVAL::FAILED_AUCTION_RECLAIM** (total=24560): auction_not_detected=12098, reclaim_hold_failed=5821, tail_too_small=4312, basic_filters_failed=2304, regime_blocked=25
- **EVAL::FUNDING_EXTREME** (total=28851): funding_not_extreme=23974, basic_filters_failed=2433, missing_funding_rate=1003, ema_alignment_reject=802, rsi_reject=454, momentum_reject=85, cvd_divergence_failed=84, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=28727): cascade_threshold_not_met=25435, basic_filters_failed=2503, cvd_divergence_failed=386, rsi_reject=385, missing_fvg_or_orderblock=13, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=25896): no_ma_cross=23191, basic_filters_failed=2305, ma_cross_cooldown=400
- **EVAL::OPENING_RANGE_BREAKOUT** (total=28768): feature_disabled=28768
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=25841): regime_blocked=10646, breakout_not_found=7235, ema_alignment_reject=3930, adx_reject=2783, basic_filters_failed=1247
- **EVAL::QUIET_COMPRESSION_BREAK** (total=25736): regime_blocked=15163, compression_not_detected=9475, basic_filters_failed=1057, breakout_not_detected=40, volume_confirmation_failed=1
- **EVAL::SR_FLIP_RETEST** (total=23672): retest_out_of_zone=9662, reclaim_hold_failed=5385, flip_close_not_confirmed=5369, basic_filters_failed=2303, wick_quality_failed=619, ema_alignment_reject=205, missing_fvg_or_orderblock=104, regime_blocked=25
- **EVAL::STANDARD** (total=23177): adx_reject=7088, momentum_reject=5219, ema_alignment_reject=3995, sweeps_not_detected=2327, macd_reject=2288, basic_filters_failed=1894, invalid_sl_geometry=329, rsi_reject=37
- **EVAL::TREND_PULLBACK** (total=25281): ema_alignment_reject=5353, h1_pullback_not_confirmed=5171, h1_trend_not_aligned=4745, ema_not_tested_prev=3680, no_ema_reclaim_close=1949, body_conviction_fail=1147, basic_filters_failed=1057, rsi_reject=984, prev_already_below_emas=371, prev_already_above_emas=190, regime_blocked=177, no_prev_low_break=171, no_prev_high_break=128, momentum_flat=79, ema21_not_tagged=38, missing_fvg_or_orderblock=21, momentum_reject=20
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=28677): breakout_not_found=21591, retest_proximity_failed=3541, basic_filters_failed=2503, volume_spike_missing=778, ema_alignment_reject=169, missing_fvg_or_orderblock=92, rsi_reject=3
- **EVAL::WHALE_MOMENTUM** (total=28728): momentum_reject=20820, recent_ticks_insufficient=7238, basic_filters_failed=670

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 36016 | 38.4% |
| RANGING | 21108 | 22.5% |
| TRENDING_UP | 18963 | 20.2% |
| QUIET | 17713 | 18.9% |
| VOLATILE | 89 | 0.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **307**
- Average confidence gap to threshold: **15.15** (samples=307) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: 1000PEPEUSDT=15, CLUSDT=15, PIEVERSEUSDT=13, ASTERUSDT=13, STGUSDT=12, CRCLUSDT=12, JTOUSDT=12, HOMEUSDT=11, MSTRUSDT=10, PUMPUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 34 |
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 4 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 313 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 134 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 18 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 451 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 93 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 43 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 250 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 102 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 97 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 323 |
| SR_FLIP_RETEST | filtered | min_confidence | 782 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 124 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1370 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 87 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 17 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 9 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 12 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 2 |
| WHALE_MOMENTUM | filtered | min_confidence | 1 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 38 | 58.75 | 65.00 | 6.25 | 20.54 | 19.71 | 19.62 | 0.00 | 8.11 |
| BREAKDOWN_SHORT | kept | 313 | 67.63 | 65.00 | -2.63 | 20.68 | 19.93 | 19.12 | 0.00 | 0.26 |
| DIVERGENCE_CONTINUATION | filtered | 152 | 57.83 | 65.00 | 7.17 | 21.43 | 19.76 | 17.90 | 1.99 | 9.21 |
| DIVERGENCE_CONTINUATION | kept | 451 | 70.48 | 65.00 | -5.48 | 21.13 | 19.78 | 18.63 | 2.34 | -0.66 |
| FAILED_AUCTION_RECLAIM | filtered | 136 | 53.91 | 65.00 | 11.09 | 20.47 | 18.91 | 20.00 | 4.43 | 7.24 |
| FAILED_AUCTION_RECLAIM | kept | 250 | 72.22 | 65.00 | -7.22 | 20.81 | 19.29 | 20.00 | 4.36 | 1.12 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 60.33 | 65.00 | 4.67 | 21.71 | 19.97 | 17.43 | 1.43 | 5.57 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 68.00 | 65.00 | -3.00 | 19.50 | 19.80 | 17.00 | 2.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 199 | 52.58 | 65.00 | 12.42 | 21.18 | 19.58 | 18.29 | 2.93 | 9.99 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 323 | 69.84 | 65.00 | -4.84 | 20.99 | 19.61 | 18.01 | 2.55 | 0.53 |
| SR_FLIP_RETEST | filtered | 906 | 55.68 | 65.00 | 9.32 | 21.13 | 19.86 | 16.37 | 1.70 | 9.32 |
| SR_FLIP_RETEST | kept | 1370 | 71.71 | 65.00 | -6.71 | 21.33 | 19.92 | 16.42 | 1.83 | 0.41 |
| TREND_PULLBACK_EMA | filtered | 9 | 62.20 | 65.00 | 2.80 | 21.09 | 19.07 | 18.26 | 5.17 | -0.27 |
| TREND_PULLBACK_EMA | kept | 87 | 75.42 | 65.00 | -10.42 | 21.65 | 19.76 | 18.47 | 5.33 | -0.98 |
| VOLUME_SURGE_BREAKOUT | filtered | 26 | 47.81 | 65.00 | 17.19 | 20.40 | 19.21 | 19.98 | 3.54 | 14.37 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 71.91 | 65.00 | -6.91 | 21.10 | 19.00 | 19.91 | 3.08 | 3.41 |
| WHALE_MOMENTUM | filtered | 3 | 58.87 | 65.00 | 6.13 | 24.67 | 20.00 | 17.00 | 0.00 | 13.87 |
| WHALE_MOMENTUM | kept | 1 | 77.30 | 65.00 | -12.30 | 19.90 | 17.90 | 17.00 | 0.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 38 | 58.75 | 20.21 | 15.37 | 5.29 | 13.05 | 4.75 | 8.18 | 0.00 |
| BREAKDOWN_SHORT | kept | 313 | 67.63 | 24.41 | 10.27 | 5.76 | 13.72 | 7.79 | 5.96 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 152 | 57.83 | 21.26 | 16.22 | 4.48 | 11.81 | 5.53 | 8.32 | 1.99 |
| DIVERGENCE_CONTINUATION | kept | 451 | 70.48 | 20.53 | 17.14 | 4.15 | 11.96 | 6.03 | 9.18 | 2.34 |
| FAILED_AUCTION_RECLAIM | filtered | 136 | 53.91 | 21.71 | 15.03 | 7.61 | 10.98 | 6.56 | 5.09 | 4.43 |
| FAILED_AUCTION_RECLAIM | kept | 250 | 72.22 | 22.18 | 15.79 | 5.06 | 11.67 | 6.71 | 7.76 | 4.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 60.33 | 25.00 | 8.00 | 8.14 | 11.57 | 5.71 | 8.19 | 1.43 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 68.00 | 25.00 | 8.00 | 6.00 | 14.00 | 5.00 | 8.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 199 | 52.58 | 22.60 | 14.18 | 6.56 | 12.62 | 5.45 | 5.73 | 2.93 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 323 | 69.84 | 22.89 | 14.66 | 5.10 | 12.44 | 5.33 | 7.43 | 2.55 |
| SR_FLIP_RETEST | filtered | 906 | 55.68 | 19.49 | 16.63 | 5.11 | 13.04 | 5.85 | 7.85 | 1.70 |
| SR_FLIP_RETEST | kept | 1370 | 71.71 | 20.41 | 17.13 | 5.27 | 13.88 | 6.15 | 8.96 | 1.83 |
| TREND_PULLBACK_EMA | filtered | 9 | 62.20 | 23.22 | 18.00 | 3.00 | 14.00 | 5.00 | 6.54 | 5.17 |
| TREND_PULLBACK_EMA | kept | 87 | 75.42 | 19.21 | 18.00 | 3.45 | 14.01 | 6.69 | 9.31 | 5.33 |
| VOLUME_SURGE_BREAKOUT | filtered | 26 | 47.81 | 23.46 | 10.69 | 7.62 | 13.54 | 5.12 | 6.87 | 3.54 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 71.91 | 19.67 | 17.17 | 6.75 | 16.00 | 3.54 | 9.11 | 3.08 |
| WHALE_MOMENTUM | filtered | 3 | 58.87 | 25.00 | 11.33 | 6.00 | 15.33 | 6.17 | 8.90 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 77.30 | 23.00 | 18.00 | 12.00 | 10.00 | 5.00 | 9.30 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 38 | 58.75 | 0.00 | 0.00 | 1.14 | 0.00 | 2.27 | 0.16 | 0.00 | 0.00 | **3.57** |
| BREAKDOWN_SHORT | kept | 313 | 67.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 152 | 57.83 | 0.00 | 0.00 | 1.91 | 0.00 | 0.82 | 0.08 | 0.00 | 0.00 | **2.81** |
| DIVERGENCE_CONTINUATION | kept | 451 | 70.48 | 0.00 | 0.00 | 0.31 | 0.00 | 0.08 | 0.05 | 0.00 | 0.00 | **0.44** |
| FAILED_AUCTION_RECLAIM | filtered | 136 | 53.91 | 0.00 | 0.00 | 0.49 | 0.00 | 4.16 | 0.00 | 0.00 | 0.00 | **4.65** |
| FAILED_AUCTION_RECLAIM | kept | 250 | 72.22 | 0.00 | 0.00 | 0.24 | 0.00 | 0.53 | 0.02 | 0.00 | 0.00 | **0.79** |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 60.33 | 0.00 | 0.00 | 5.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.49** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 199 | 52.58 | 0.08 | 0.00 | 1.60 | 0.00 | 7.32 | 0.10 | 0.00 | 0.00 | **9.10** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 323 | 69.84 | 0.00 | 0.00 | 0.19 | 0.00 | 0.28 | 0.04 | 0.00 | 0.00 | **0.51** |
| SR_FLIP_RETEST | filtered | 906 | 55.68 | 0.00 | 0.00 | 0.94 | 0.00 | 2.24 | 0.01 | 0.00 | 0.52 | **3.71** |
| SR_FLIP_RETEST | kept | 1370 | 71.71 | 0.00 | 0.00 | 0.16 | 0.00 | 0.37 | 0.03 | 0.00 | 0.00 | **0.56** |
| TREND_PULLBACK_EMA | filtered | 9 | 62.20 | 0.00 | 0.00 | 1.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.07** |
| TREND_PULLBACK_EMA | kept | 87 | 75.42 | 0.00 | 0.00 | 0.55 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.63** |
| VOLUME_SURGE_BREAKOUT | filtered | 26 | 47.81 | 0.00 | 0.00 | 2.22 | 0.00 | 5.28 | 0.00 | 0.00 | 1.66 | **9.16** |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 71.91 | 0.00 | 0.00 | 0.80 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **1.16** |
| WHALE_MOMENTUM | filtered | 3 | 58.87 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| WHALE_MOMENTUM | kept | 1 | 77.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=54 (78.3%) | PREMATURE=10 (14.5%) | NEUTRAL=5 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 44 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 14 | 4 | 0 | 0 |
| momentum_loss | 23 | 5 | 1 | 0 |
| regime_shift | 6 | 0 | 1 | 0 |
| trailing_invalidation | 11 | 1 | 3 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 4 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 0 | 1 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 19 | 5 | 1 | 0 |
| SR_FLIP_RETEST | 17 | 4 | 2 | 0 |
| TREND_PULLBACK_EMA | 2 | 1 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 14 | 4 | 0 | 4.6 | 7.8 | -0.18 | **INSUFFICIENT_SAMPLE** — only 18 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 23 | 5 | 1 | 14.1 | 8.1 | +0.20 | **KEEP** — net-helping: avg +0.21R/kill across 29 kills (saved 14.1R vs missed 8.1R) |
| regime_shift | 6 | 0 | 1 | 4.2 | 0.0 | +0.60 | **INSUFFICIENT_SAMPLE** — only 7 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 11 | 1 | 3 | 8.7 | 1.2 | +0.50 | **INSUFFICIENT_SAMPLE** — only 15 classified kills (need >= 20); let data accumulate before tuning |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `697804`
- `Path funnel` emissions: `13`
- `Regime distribution` emissions: `13`
- `QUIET_SCALP_BLOCK` events: `307`
- `confidence_gate` events: `4284`
- `free_channel_post` events: `145`
- `pre_tp_fire` events: `68`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **68**
- Avg resolved threshold: **0.505%** raw → avg net **+4.35%** @ 10x
- Avg time-to-fire from dispatch: **217s**
- By threshold source: stamped=68

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 27 | 0.482% | +4.12% | 239 | stamped=27 |
| LIQUIDITY_SWEEP_REVERSAL | 25 | 0.557% | +4.87% | 220 | stamped=25 |
| FAILED_AUCTION_RECLAIM | 6 | 0.491% | +4.21% | 270 | stamped=6 |
| DIVERGENCE_CONTINUATION | 5 | 0.426% | +3.56% | 118 | stamped=5 |
| TREND_PULLBACK_EMA | 5 | 0.461% | +3.91% | 122 | stamped=5 |
- Top symbols: PUMPUSDT=7, RENDERUSDT=7, FILUSDT=7, OPGUSDT=6, STGUSDT=5, PIEVERSEUSDT=4, XPLUSDT=3, ALLOUSDT=3, HOMEUSDT=3, VICUSDT=3

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **145**

| Source | Count |
|---|---:|
| signal_close | 75 |
| pre_tp | 68 |
| signal_highlight | 2 |

- By severity: HIGH=145

## Dependency readiness
- cvd: presence[present=84227] state[populated=84227] buckets[many=84227] sources[none] quality[none]
- funding_rate: presence[absent=2293, present=81934] state[empty=2293, populated=81934] buckets[few=81934, none=2293] sources[none] quality[none]
- liquidation_clusters: presence[absent=27886, present=56341] state[empty=27886, populated=56341] buckets[few=36851, none=27886, some=19490] sources[none] quality[none]
- oi_snapshot: presence[absent=1325, present=82902] state[empty=1325, populated=82902] buckets[many=82902, none=1325] sources[none] quality[none]
- order_book: presence[absent=55320, present=28907] state[populated=28907, unavailable=55320] buckets[few=28907, none=55320] sources[book_ticker=28907, unavailable=55320] quality[none=55320, top_of_book_only=28907]
- orderblocks: presence[absent=84227] state[empty=84227] buckets[none=84227] sources[not_implemented=84227] quality[none]
- recent_ticks: presence[present=84227] state[populated=84227] buckets[many=84227] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `19.784068942070007` sec
- Median create→first breach: `366.1170630455017` sec
- Median create→terminal: `356.8961889743805` sec
- Median first breach→terminal: `4.690161943435669` sec
- Fast-failure buckets: `{"under_120s": {"count": 14, "pct": 18.7}, "under_180s": {"count": 19, "pct": 25.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 6, "pct": 8.0}}`
- ~3 minute terminal-close behavior: `{"count": 10, "pct": 6.8}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 4 | 0.0 | 25.0 | 0.0 | 0.0 | -0.3523 | 69.87745904922485 | 424.5470914840698 |
| DIVERGENCE_CONTINUATION | 12 | 12 | 0.0 | 8.3 | 0.0 | 41.7 | 0.0529 | 271.32361006736755 | 144.74172401428223 |
| FAILED_AUCTION_RECLAIM | 14 | 14 | 0.0 | 7.1 | 0.0 | 42.9 | -0.0437 | 192.15959405899048 | 471.2759510278702 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -1.9058 | None | 133.67719101905823 |
| LIQUIDITY_SWEEP_REVERSAL | 49 | 49 | 0.0 | 4.1 | 0.0 | 51.0 | 0.0497 | 352.5807235240936 | 347.1223158836365 |
| SR_FLIP_RETEST | 57 | 57 | 0.0 | 12.3 | 0.0 | 47.4 | -0.0438 | 437.9415240287781 | 400.2408571243286 |
| TREND_PULLBACK_EMA | 8 | 8 | 0.0 | 0.0 | 0.0 | 62.5 | 0.0745 | 354.13648200035095 | 494.2131019830704 |
| WHALE_MOMENTUM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.3165 | None | 141.22114205360413 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 5594 | 288 | 2399 | 0.0 | 12.3 | 437.9415240287781 | 400.2408571243286 | 3195 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 748 | 18 | 642 | 0.0 | 0.0 | 354.13648200035095 | 494.2131019830704 | 106 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `44`
- Gating Δ: `2689`
- No-generation Δ: `88431`
- Fast failures Δ: `19`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.6099, "current_avg_pnl": -0.3523, "current_win_rate": 0.0, "previous_avg_pnl": 0.2576, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0529, "current_avg_pnl": 0.0529, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0437, "current_avg_pnl": -0.0437, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.2614, "current_avg_pnl": 0.0497, "current_win_rate": 0.0, "previous_avg_pnl": -0.2117, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.3289, "current_avg_pnl": -0.0438, "current_win_rate": 0.0, "previous_avg_pnl": 0.2851, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.0745, "current_avg_pnl": 0.0745, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -20, "geometry_changed_delta": 0, "geometry_preserved_delta": -777, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -799.98, "median_terminal_delta_sec": -843.06, "sl_rate_delta": 12.3, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 25, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 354.14, "median_terminal_delta_sec": 494.21, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDATION_REVERSAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
