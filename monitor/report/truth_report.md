# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `4805` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 18 | 18 | 18 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 7118 | 7118 | 6403 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 51017 | 51017 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 39060 | 39062 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 38987 | 36687 | 2372 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 39064 | 37247 | 1873 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 43404 | 43371 | 36 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 36590 | 36590 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 39120 | 39125 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 55789 | 54978 | 3319 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 51021 | 41106 | 14672 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 42761 | 42762 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 39061 | 39065 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 38985 | 38940 | 47 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 38339 | 37486 | 1493 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 32355 | 30686 | 1743 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 32429 | 32211 | 235 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 51013 | 51009 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 36590 | 36540 | 62 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6088 | 6088 | 4480 | 25 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 85 | 85 | 72 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8783 | 8783 | 8295 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 1 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 5654 | 5654 | 4956 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 35388 | 35388 | 31967 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 109 | 109 | 63 | 2 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 4226 | 4226 | 1208 | 40 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1093 | 1093 | 1089 | 3 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 27 | 27 | 0 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2209 | 2209 | 1987 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=51017): breakout_not_found=23983, basic_filters_failed=19000, move_not_fresh=4200, breakout_stale=3539, retest_proximity_failed=208, volume_spike_missing=85, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=39062): cls_disabled_merged_into_lsr=39062
- **EVAL::DIVERGENCE_CONTINUATION** (total=36687): cvd_divergence_failed=13846, basic_filters_failed=12337, ema_alignment_reject=6396, h1_trend_not_aligned=3298, retest_proximity_failed=562, missing_fvg_or_orderblock=153, regime_blocked=95
- **EVAL::FAILED_AUCTION_RECLAIM** (total=37247): auction_not_detected=12884, basic_filters_failed=12110, tail_too_small=6079, reclaim_hold_failed=5676, regime_blocked=498
- **EVAL::FUNDING_EXTREME** (total=43371): funding_not_extreme=29549, basic_filters_failed=12253, missing_funding_rate=1268, ema_alignment_reject=112, rsi_reject=72, cvd_divergence_failed=66, momentum_reject=49, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=36590): cascade_threshold_not_met=23365, basic_filters_failed=12979, rsi_reject=120, cvd_divergence_failed=119, missing_fvg_or_orderblock=5, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=39125): no_ma_cross=26250, basic_filters_failed=12342, ma_cross_cooldown=464, ma_cross_htf_misaligned=52, ma_cross_htf_unconfirmed=17
- **EVAL::MOVER_AVWAP_SCALP** (total=54978): no_avwap_tag=27751, basic_filters_failed=19024, no_mover_leg=5906, avwap_slope_against=1721, no_avwap_reclaim=352, avwap_reclaim_no_volume=224
- **EVAL::MOVER_TREND_PULLBACK** (total=41106): basic_filters_failed=19011, mover_run_too_small=14096, no_reclaim=5754, no_pullback_tag=2245
- **EVAL::OPENING_RANGE_BREAKOUT** (total=42762): feature_disabled=42762
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=39065): regime_blocked=27840, breakout_not_found=6640, basic_filters_failed=3666, adx_reject=897, ema_alignment_reject=22
- **EVAL::QUIET_COMPRESSION_BREAK** (total=38940): compression_not_detected=17035, regime_blocked=11714, basic_filters_failed=8442, breakout_not_detected=1652, volume_confirmation_failed=60, rsi_reject=37
- **EVAL::SR_FLIP_RETEST** (total=37486): basic_filters_failed=12104, whipsaw_flip=6594, long_break_volume_thin=4432, flip_close_not_confirmed=4375, reclaim_hold_failed=4041, long_disabled=2433, retest_out_of_zone=2083, regime_blocked=497, wick_quality_failed=453, long_acceptance_not_held=298, missing_fvg_or_orderblock=102, ema_alignment_reject=66, rsi_reject=8
- **EVAL::STANDARD** (total=30686): momentum_reject=8527, adx_reject=7510, basic_filters_failed=7354, sweeps_not_detected=3551, macd_reject=2081, ema_alignment_reject=1558, invalid_sl_geometry=58, rsi_reject=47
- **EVAL::TREND_PULLBACK** (total=32211): basic_filters_failed=7627, h1_pullback_not_confirmed=7259, ema_alignment_reject=5138, h1_trend_not_aligned=4662, no_ema_reclaim_close=2112, ema_not_tested_prev=1688, body_conviction_fail=1271, regime_blocked=828, rsi_reject=811, prev_already_below_emas=372, no_prev_low_break=183, prev_already_above_emas=116, no_prev_high_break=60, momentum_flat=48, missing_fvg_or_orderblock=17, ema21_not_tagged=13, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=51009): breakout_not_found=24719, basic_filters_failed=19000, move_not_fresh=5143, breakout_stale=1371, retest_proximity_failed=374, move_exhausted=180, ema_alignment_reject=164, volume_spike_missing=58
- **EVAL::WHALE_MOMENTUM** (total=36540): momentum_reject=19936, recent_ticks_insufficient=10463, basic_filters_failed=6141

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 88007 | 37.6% |
| QUIET | 53516 | 22.9% |
| TRENDING_UP | 44566 | 19.1% |
| TRENDING_DOWN | 37502 | 16.0% |
| VOLATILE | 10337 | 4.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **160**
- Average confidence gap to threshold: **11.88** (samples=160) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: NBISUSDT=28, XRPUSDT=22, TRXUSDT=19, BNBUSDT=18, BTCUSDT=14, AAVEUSDT=11, DOGEUSDT=10, AMDUSDT=9, 1000PEPEUSDT=6, LTCUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 44 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 200 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 79 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 30 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 487 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 15 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 225 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 479 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 28 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 124 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 40 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1849 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 46 |
| SR_FLIP_RETEST | filtered | min_confidence | 211 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 39 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 932 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 4 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 18 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |
| WHALE_MOMENTUM | filtered | min_confidence | 11 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 8 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 44 | 57.88 | 65.00 | 7.12 | 20.74 | 19.97 | 17.09 | 2.36 | 9.66 |
| DIVERGENCE_CONTINUATION | kept | 200 | 70.58 | 65.00 | -5.58 | 19.99 | 19.91 | 17.14 | 2.54 | -0.81 |
| FAILED_AUCTION_RECLAIM | filtered | 109 | 46.84 | 65.00 | 18.16 | 20.12 | 19.53 | 20.00 | 3.98 | 13.95 |
| FAILED_AUCTION_RECLAIM | kept | 487 | 70.23 | 65.00 | -5.23 | 21.58 | 19.66 | 20.00 | 3.99 | 0.92 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 53.81 | 65.00 | 11.19 | 20.62 | 20.00 | 17.23 | 1.50 | 18.55 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 225 | 70.00 | 65.00 | -5.00 | 22.43 | 19.79 | 17.40 | 2.32 | -0.01 |
| MOVER_AVWAP_SCALP | filtered | 507 | 59.41 | 65.00 | 5.59 | 17.62 | 18.46 | 15.80 | 2.56 | 3.13 |
| MOVER_AVWAP_SCALP | kept | 124 | 71.83 | 65.00 | -6.83 | 18.87 | 18.45 | 15.80 | 4.27 | 7.39 |
| MOVER_TREND_PULLBACK | filtered | 45 | 59.70 | 65.00 | 5.30 | 22.11 | 19.47 | 15.80 | 4.31 | 20.09 |
| MOVER_TREND_PULLBACK | kept | 1849 | 75.73 | 65.00 | -10.73 | 21.72 | 19.33 | 15.80 | 4.55 | 1.63 |
| QUIET_COMPRESSION_BREAK | kept | 46 | 72.30 | 65.00 | -7.30 | 18.96 | 20.00 | 20.00 | 0.00 | 4.21 |
| SR_FLIP_RETEST | filtered | 250 | 59.62 | 65.00 | 5.38 | 21.17 | 19.93 | 15.51 | 1.51 | 9.25 |
| SR_FLIP_RETEST | kept | 932 | 70.01 | 65.00 | -5.01 | 21.30 | 19.95 | 15.38 | 2.06 | -0.80 |
| TREND_PULLBACK_EMA | kept | 4 | 80.12 | 65.00 | -15.12 | 20.77 | 18.95 | 18.35 | 4.75 | -3.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 54.04 | 65.00 | 10.96 | 20.66 | 17.73 | 20.00 | 4.39 | 12.99 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.15 | 65.00 | -13.15 | 20.70 | 19.60 | 20.00 | 4.75 | 5.45 |
| WHALE_MOMENTUM | filtered | 19 | 46.51 | 65.00 | 18.49 | 24.30 | 20.00 | 17.00 | 0.00 | 19.09 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 44 | 57.88 | 19.91 | 13.00 | 5.45 | 12.84 | 6.73 | 8.26 | 2.36 |
| DIVERGENCE_CONTINUATION | kept | 200 | 70.58 | 24.32 | 15.80 | 4.20 | 11.34 | 5.44 | 7.94 | 2.54 |
| FAILED_AUCTION_RECLAIM | filtered | 109 | 46.84 | 20.61 | 15.76 | 5.78 | 12.19 | 5.95 | 4.77 | 3.98 |
| FAILED_AUCTION_RECLAIM | kept | 487 | 70.23 | 21.01 | 14.61 | 5.37 | 11.91 | 6.59 | 7.67 | 3.99 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 53.81 | 18.91 | 14.00 | 12.00 | 13.18 | 5.00 | 7.76 | 1.50 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 225 | 70.00 | 22.45 | 14.37 | 4.25 | 12.15 | 6.00 | 8.46 | 2.32 |
| MOVER_AVWAP_SCALP | filtered | 507 | 59.41 | 22.67 | 18.00 | 7.54 | 13.86 | 3.53 | 4.82 | 2.56 |
| MOVER_AVWAP_SCALP | kept | 124 | 71.83 | 20.95 | 18.00 | 10.38 | 13.35 | 6.35 | 5.95 | 4.27 |
| MOVER_TREND_PULLBACK | filtered | 45 | 59.70 | 18.29 | 18.00 | 8.70 | 15.53 | 6.30 | 8.65 | 4.31 |
| MOVER_TREND_PULLBACK | kept | 1849 | 75.73 | 19.09 | 18.00 | 8.01 | 13.81 | 5.49 | 8.41 | 4.55 |
| QUIET_COMPRESSION_BREAK | kept | 46 | 72.30 | 17.00 | 18.00 | 9.13 | 14.00 | 8.42 | 9.96 | 0.00 |
| SR_FLIP_RETEST | filtered | 250 | 59.62 | 18.75 | 16.44 | 4.87 | 13.12 | 5.57 | 8.61 | 1.51 |
| SR_FLIP_RETEST | kept | 932 | 70.01 | 21.74 | 14.41 | 4.36 | 13.53 | 6.08 | 9.13 | 2.06 |
| TREND_PULLBACK_EMA | kept | 4 | 80.12 | 19.00 | 18.00 | 7.50 | 14.75 | 7.62 | 8.50 | 4.75 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 54.04 | 18.78 | 18.00 | 12.00 | 11.00 | 5.00 | 4.53 | 4.39 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.15 | 21.00 | 18.00 | 13.50 | 14.00 | 5.00 | 7.35 | 4.75 |
| WHALE_MOMENTUM | filtered | 19 | 46.51 | 25.00 | 8.00 | 7.26 | 11.47 | 5.00 | 8.86 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 44 | 57.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.55 | 0.00 | 0.00 | 0.00 | **0.55** |
| DIVERGENCE_CONTINUATION | kept | 200 | 70.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.04** |
| FAILED_AUCTION_RECLAIM | filtered | 109 | 46.84 | 0.00 | 0.00 | 3.39 | 0.00 | 3.37 | 0.00 | 0.00 | 0.00 | **6.76** |
| FAILED_AUCTION_RECLAIM | kept | 487 | 70.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.89 | 0.00 | 0.00 | 0.00 | **0.89** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 53.81 | 0.00 | 0.00 | 0.00 | 0.00 | 18.55 | 0.00 | 0.00 | 0.00 | **18.55** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 225 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 507 | 59.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 124 | 71.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 45 | 59.70 | 0.00 | 0.00 | 0.89 | 0.00 | 19.20 | 0.00 | 0.00 | 0.00 | **20.09** |
| MOVER_TREND_PULLBACK | kept | 1849 | 75.73 | 0.00 | 0.00 | 0.30 | 0.00 | 0.39 | 0.00 | 0.00 | 0.00 | **0.69** |
| QUIET_COMPRESSION_BREAK | kept | 46 | 72.30 | 0.00 | 0.00 | 0.00 | 0.00 | 4.21 | 0.00 | 0.00 | 0.00 | **4.21** |
| SR_FLIP_RETEST | filtered | 250 | 59.62 | 0.00 | 0.00 | 0.00 | 0.00 | 2.51 | 0.00 | 0.00 | 0.00 | **2.51** |
| SR_FLIP_RETEST | kept | 932 | 70.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.04** |
| TREND_PULLBACK_EMA | kept | 4 | 80.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 54.04 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 1.60 | **4.27** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.15 | 0.00 | 0.00 | 0.00 | 0.00 | 2.15 | 0.00 | 0.00 | 1.80 | **3.95** |
| WHALE_MOMENTUM | filtered | 19 | 46.51 | 0.00 | 0.00 | 0.00 | 0.00 | 9.09 | 0.00 | 0.00 | 0.00 | **9.09** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=66 (71.7%) | PREMATURE=12 (13.0%) | NEUTRAL=14 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 54 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 66 | 12 | 14 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 14 | 4 | 7 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 1 | 1 | 0 |
| MOVER_AVWAP_SCALP | 13 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 24 | 1 | 1 | 0 |
| SR_FLIP_RETEST | 9 | 3 | 4 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 66 | 12 | 14 | 50.4 | 16.0 | +0.37 | **KEEP** — net-helping: avg +0.37R/kill across 92 kills (saved 50.4R vs missed 16.0R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `83967`
- `Path funnel` emissions: `24`
- `Regime distribution` emissions: `24`
- `QUIET_SCALP_BLOCK` events: `160`
- `confidence_gate` events: `4883`
- `free_channel_post` events: `7`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 1973 | 1973 | 1973 | 0 |
| futures_liq | 3 | 7174 | 7174 | 9951 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **7**

| Source | Count |
|---|---:|
| signal_close | 4 |
| regime_shift | 3 |

- By severity: HIGH=7

## Dependency readiness
- cvd: presence[present=166561] state[populated=166561] buckets[many=164552, some=2009] sources[none] quality[none]
- funding_rate: presence[absent=33183, present=133378] state[empty=33183, populated=133378] buckets[few=133378, none=33183] sources[none] quality[none]
- liquidation_clusters: presence[absent=122068, present=44493] state[empty=122068, populated=44493] buckets[few=37779, none=122068, some=6714] sources[none] quality[none]
- oi_snapshot: presence[absent=33183, present=133378] state[empty=33183, populated=133378] buckets[many=133378, none=33183] sources[none] quality[none]
- order_book: presence[absent=46469, present=120092] state[populated=120092, unavailable=46469] buckets[few=120092, none=46469] sources[book_ticker=120092, unavailable=46469] quality[none=46469, top_of_book_only=120092]
- orderblocks: presence[absent=166561] state[empty=166561] buckets[none=166561] sources[not_implemented=166561] quality[none]
- recent_ticks: presence[present=166561] state[populated=166561] buckets[many=166561] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.695954442024231` sec
- Median create→first breach: `1130.6680319309235` sec
- Median create→terminal: `2486.0044820308685` sec
- Median first breach→terminal: `2.3869290351867676` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1824 | 1368.5721039772034 | 1370.5175740718842 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 0.7454 | 22369.10111784935 | 12987.499123930931 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.3886 | 892.7639598846436 | 895.7945709228516 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.025 | None | 3601.491389989853 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.4424 | 725.3419208526611 | 725.8101480007172 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.7061 | 2200.57363653183 | 2202.9326030015945 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 4226 | 40 | 1208 | 100.0 | 0.0 | 725.3419208526611 | 725.8101480007172 | 3018 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1093 | 3 | 1089 | 0.0 | 0.0 | None | None | 4 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `99`
- Gating Δ: `60539`
- No-generation Δ: `687882`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -1.668, "current_avg_pnl": -1.1824, "current_win_rate": 0.0, "previous_avg_pnl": 0.4856, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.5609, "current_avg_pnl": 0.7454, "current_win_rate": 0.0, "previous_avg_pnl": 1.3063, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.5106, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.5106, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 1.6845, "current_avg_pnl": 1.4424, "current_win_rate": 100.0, "previous_avg_pnl": -0.2421, "previous_win_rate": 14.3, "win_rate_delta": 85.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 40, "geometry_changed_delta": 0, "geometry_preserved_delta": 3018, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -228.6, "median_terminal_delta_sec": -545.84, "sl_rate_delta": -57.1, "win_rate_delta": 85.7}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 4, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
