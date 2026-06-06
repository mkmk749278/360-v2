# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `564` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 3307 | 3307 | 884 | 17 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 37615 | 37615 | 26872 | 113 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 150486 | 149740 | 808 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 125246 | 125257 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 124441 | 116972 | 8254 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 125292 | 120349 | 5229 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 151420 | 150772 | 742 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 150405 | 150410 | 10 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 125581 | 125618 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 150550 | 150553 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 125264 | 125287 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 124414 | 124396 | 42 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 123467 | 118780 | 5541 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 122601 | 108423 | 14831 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 123261 | 122449 | 902 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 150429 | 149760 | 724 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 150419 | 150426 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 19488 | 19488 | 16028 | 68 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2998 | 2998 | 2496 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 15 | 15 | 15 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 60190 | 60190 | 53055 | 201 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 6 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 57 | 57 | 47 | 3 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 26671 | 26671 | 11010 | 252 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4587 | 4587 | 4306 | 6 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2411 | 2411 | 1162 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=149740): breakout_not_found=73746, retest_proximity_failed=34628, basic_filters_failed=33774, volume_spike_missing=6084, ema_alignment_reject=717, missing_fvg_or_orderblock=486, insufficient_candles=305
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=125257): cls_disabled_merged_into_lsr=125257
- **EVAL::DIVERGENCE_CONTINUATION** (total=116972): cvd_divergence_failed=59907, basic_filters_failed=25558, ema_alignment_reject=13449, h1_trend_not_aligned=13287, retest_proximity_failed=3786, missing_fvg_or_orderblock=725, regime_blocked=260
- **EVAL::FAILED_AUCTION_RECLAIM** (total=120349): auction_not_detected=43634, basic_filters_failed=23597, reclaim_hold_failed=22720, tail_too_small=18518, regime_blocked=11880
- **EVAL::FUNDING_EXTREME** (total=150772): funding_not_extreme=101365, basic_filters_failed=32704, missing_funding_rate=8015, ema_alignment_reject=5032, rsi_reject=2392, cvd_divergence_failed=641, momentum_reject=453, missing_fvg_or_orderblock=113, insufficient_candles=57
- **EVAL::LIQUIDATION_REVERSAL** (total=150410): cascade_threshold_not_met=113744, basic_filters_failed=33772, cvd_divergence_failed=1379, rsi_reject=1176, insufficient_candles=242, missing_fvg_or_orderblock=71, volume_spike_missing=26
- **EVAL::MA_CROSS_TREND_SHIFT** (total=125618): no_ma_cross=99395, basic_filters_failed=25569, ma_cross_cooldown=654
- **EVAL::OPENING_RANGE_BREAKOUT** (total=150553): feature_disabled=150553
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=125287): regime_blocked=94843, breakout_not_found=25545, basic_filters_failed=4849, adx_reject=28, ema_alignment_reject=17, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=124396): compression_not_detected=60074, regime_blocked=42072, basic_filters_failed=18741, breakout_not_detected=3044, volume_confirmation_failed=439, rsi_reject=26
- **EVAL::SR_FLIP_RETEST** (total=118780): retest_out_of_zone=37798, flip_close_not_confirmed=23999, basic_filters_failed=23588, reclaim_hold_failed=18149, regime_blocked=11806, wick_quality_failed=2514, ema_alignment_reject=469, missing_fvg_or_orderblock=409, rsi_reject=48
- **EVAL::STANDARD** (total=108423): basic_filters_failed=22379, macd_reject=21130, momentum_reject=19703, ema_alignment_reject=17711, adx_reject=15155, sweeps_not_detected=8750, invalid_sl_geometry=3373, rsi_reject=203, mtf_reject=19
- **EVAL::TREND_PULLBACK** (total=122449): h1_pullback_not_confirmed=32704, ema_alignment_reject=21039, ema_not_tested_prev=19288, h1_trend_not_aligned=16566, basic_filters_failed=14656, no_ema_reclaim_close=7429, rsi_reject=4074, body_conviction_fail=3121, prev_already_below_emas=1706, no_prev_low_break=942, regime_blocked=435, prev_already_above_emas=176, ema21_not_tagged=107, no_prev_high_break=70, momentum_flat=67, missing_fvg_or_orderblock=42, momentum_reject=27
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=149760): breakout_not_found=103810, basic_filters_failed=33773, retest_proximity_failed=8697, volume_spike_missing=2596, ema_alignment_reject=379, insufficient_candles=305, missing_fvg_or_orderblock=184, rsi_reject=16
- **EVAL::WHALE_MOMENTUM** (total=150426): momentum_reject=121707, recent_ticks_insufficient=18503, basic_filters_failed=10216

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 456824 | 57.4% |
| TRENDING_DOWN | 118462 | 14.9% |
| VOLATILE | 100313 | 12.6% |
| QUIET | 69577 | 8.7% |
| TRENDING_UP | 50366 | 6.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **312**
- Average confidence gap to threshold: **14.68** (samples=312) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: INTCUSDT=69, CLUSDT=59, TRXUSDT=50, QQQUSDT=46, BZUSDT=38, AVGOUSDT=28, 1000PEPEUSDT=5, LTCUSDT=5, ASTERUSDT=4, BNBUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 306 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 122 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 1286 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 12 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1583 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 495 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 94 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1135 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 65 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 6 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 8 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1402 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 31 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1288 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 3 |
| SR_FLIP_RETEST | filtered | min_confidence | 4315 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 157 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3475 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 240 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 155 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 5 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 306 | 59.10 | 65.00 | 5.90 | 20.35 | 19.67 | 19.89 | 0.00 | 8.89 |
| BREAKDOWN_SHORT | kept | 122 | 68.76 | 65.00 | -3.76 | 19.84 | 19.28 | 20.00 | 0.00 | 1.83 |
| DIVERGENCE_CONTINUATION | filtered | 1298 | 58.61 | 65.00 | 6.39 | 20.34 | 19.55 | 18.83 | 2.37 | 10.30 |
| DIVERGENCE_CONTINUATION | kept | 1583 | 69.93 | 65.00 | -4.93 | 20.82 | 19.50 | 18.50 | 2.78 | 0.06 |
| FAILED_AUCTION_RECLAIM | filtered | 589 | 55.27 | 65.00 | 9.73 | 20.53 | 19.13 | 20.00 | 4.23 | 7.71 |
| FAILED_AUCTION_RECLAIM | kept | 1135 | 71.68 | 65.00 | -6.68 | 20.95 | 19.18 | 20.00 | 3.85 | 0.86 |
| FUNDING_EXTREME_SIGNAL | filtered | 71 | 56.37 | 65.00 | 8.63 | 21.06 | 20.00 | 17.00 | 0.52 | 12.15 |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 67.70 | 65.00 | -2.70 | 17.55 | 20.00 | 17.00 | 2.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1433 | 57.06 | 65.00 | 7.94 | 21.47 | 19.50 | 18.40 | 2.42 | 6.82 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1288 | 70.33 | 65.00 | -5.33 | 20.82 | 19.59 | 17.85 | 1.99 | 0.73 |
| QUIET_COMPRESSION_BREAK | filtered | 7 | 54.70 | 65.00 | 10.30 | 22.27 | 20.00 | 20.00 | 0.00 | 7.87 |
| QUIET_COMPRESSION_BREAK | kept | 3 | 74.97 | 65.00 | -9.97 | 21.03 | 19.53 | 20.00 | 0.00 | 3.90 |
| SR_FLIP_RETEST | filtered | 4472 | 56.40 | 65.00 | 8.60 | 20.66 | 19.86 | 16.04 | 1.63 | 9.29 |
| SR_FLIP_RETEST | kept | 3475 | 71.61 | 65.00 | -6.61 | 21.18 | 19.86 | 16.16 | 1.98 | 1.23 |
| TREND_PULLBACK_EMA | kept | 240 | 73.49 | 65.00 | -8.49 | 21.13 | 19.25 | 18.78 | 5.19 | 3.22 |
| VOLUME_SURGE_BREAKOUT | filtered | 160 | 53.43 | 65.00 | 11.57 | 22.36 | 19.56 | 19.76 | 3.33 | 6.98 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 68.20 | 65.00 | -3.20 | 18.70 | 20.00 | 20.00 | 1.50 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 306 | 59.10 | 22.69 | 9.65 | 7.25 | 13.27 | 5.64 | 9.50 | 0.00 |
| BREAKDOWN_SHORT | kept | 122 | 68.76 | 24.15 | 11.44 | 5.75 | 13.51 | 6.72 | 9.02 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 1298 | 58.61 | 21.75 | 12.21 | 6.20 | 12.06 | 5.63 | 8.68 | 2.37 |
| DIVERGENCE_CONTINUATION | kept | 1583 | 69.93 | 22.21 | 13.96 | 5.33 | 12.15 | 5.84 | 9.15 | 2.78 |
| FAILED_AUCTION_RECLAIM | filtered | 589 | 55.27 | 19.99 | 16.96 | 6.21 | 10.78 | 6.47 | 5.70 | 4.23 |
| FAILED_AUCTION_RECLAIM | kept | 1135 | 71.68 | 21.83 | 16.26 | 4.03 | 12.04 | 5.93 | 8.61 | 3.85 |
| FUNDING_EXTREME_SIGNAL | filtered | 71 | 56.37 | 20.61 | 12.65 | 5.75 | 15.31 | 7.32 | 7.63 | 0.52 |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 67.70 | 25.00 | 8.00 | 3.00 | 17.00 | 5.00 | 7.70 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1433 | 57.06 | 22.84 | 14.14 | 6.82 | 12.52 | 5.51 | 5.91 | 2.42 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1288 | 70.33 | 22.56 | 14.35 | 5.03 | 12.99 | 5.85 | 8.33 | 1.99 |
| QUIET_COMPRESSION_BREAK | filtered | 7 | 54.70 | 19.29 | 18.00 | 9.43 | 14.00 | 8.50 | 4.07 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 3 | 74.97 | 25.00 | 18.00 | 9.00 | 14.00 | 6.17 | 6.67 | 0.00 |
| SR_FLIP_RETEST | filtered | 4472 | 56.40 | 19.58 | 17.65 | 4.67 | 13.05 | 5.76 | 7.70 | 1.63 |
| SR_FLIP_RETEST | kept | 3475 | 71.61 | 21.20 | 16.92 | 5.15 | 13.46 | 5.73 | 9.26 | 1.98 |
| TREND_PULLBACK_EMA | kept | 240 | 73.49 | 19.30 | 18.00 | 3.11 | 14.00 | 7.23 | 9.89 | 5.19 |
| VOLUME_SURGE_BREAKOUT | filtered | 160 | 53.43 | 18.82 | 12.69 | 8.76 | 14.40 | 5.96 | 5.09 | 3.33 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 68.20 | 17.00 | 18.00 | 3.00 | 14.00 | 9.00 | 8.70 | 1.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 306 | 59.10 | 0.00 | 0.00 | 0.70 | 0.00 | 4.00 | 0.42 | 0.00 | 0.00 | **5.12** |
| BREAKDOWN_SHORT | kept | 122 | 68.76 | 0.00 | 0.00 | 0.16 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **0.36** |
| DIVERGENCE_CONTINUATION | filtered | 1298 | 58.61 | 0.00 | 0.00 | 2.69 | 0.00 | 3.02 | 0.27 | 0.00 | 0.00 | **5.98** |
| DIVERGENCE_CONTINUATION | kept | 1583 | 69.93 | 0.00 | 0.00 | 1.10 | 0.00 | 0.57 | 0.01 | 0.00 | 0.00 | **1.68** |
| FAILED_AUCTION_RECLAIM | filtered | 589 | 55.27 | 0.00 | 0.00 | 2.69 | 0.00 | 1.99 | 0.12 | 0.00 | 0.00 | **4.80** |
| FAILED_AUCTION_RECLAIM | kept | 1135 | 71.68 | 0.00 | 0.00 | 0.17 | 0.00 | 0.39 | 0.04 | 0.00 | 0.00 | **0.60** |
| FUNDING_EXTREME_SIGNAL | filtered | 71 | 56.37 | 0.00 | 0.00 | 5.58 | 0.00 | 1.99 | 0.00 | 0.00 | 0.00 | **7.57** |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 67.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1433 | 57.06 | 0.05 | 0.00 | 2.84 | 0.00 | 2.98 | 0.40 | 0.00 | 0.00 | **6.27** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1288 | 70.33 | 0.00 | 0.00 | 0.30 | 0.00 | 0.29 | 0.05 | 0.00 | 0.00 | **0.64** |
| QUIET_COMPRESSION_BREAK | filtered | 7 | 54.70 | 0.00 | 0.00 | 0.00 | 0.00 | 3.07 | 0.00 | 0.00 | 0.00 | **3.07** |
| QUIET_COMPRESSION_BREAK | kept | 3 | 74.97 | 0.00 | 0.00 | 0.00 | 0.00 | 2.87 | 0.00 | 0.00 | 0.00 | **2.87** |
| SR_FLIP_RETEST | filtered | 4472 | 56.40 | 0.00 | 0.00 | 1.20 | 0.00 | 0.96 | 0.06 | 0.00 | 0.81 | **3.03** |
| SR_FLIP_RETEST | kept | 3475 | 71.61 | 0.00 | 0.00 | 0.20 | 0.00 | 0.43 | 0.02 | 0.00 | 0.00 | **0.65** |
| TREND_PULLBACK_EMA | kept | 240 | 73.49 | 0.00 | 0.00 | 3.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.06** |
| VOLUME_SURGE_BREAKOUT | filtered | 160 | 53.43 | 0.00 | 0.00 | 1.88 | 0.00 | 1.39 | 0.00 | 0.00 | 0.16 | **3.43** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 68.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=164 (79.6%) | PREMATURE=31 (15.0%) | NEUTRAL=11 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 133 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 49 | 8 | 0 | 0 |
| ema_crossover | 0 | 0 | 1 | 0 |
| momentum_loss | 78 | 15 | 3 | 0 |
| regime_shift | 8 | 0 | 1 | 0 |
| trailing_invalidation | 29 | 8 | 6 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 9 | 2 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 26 | 4 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 15 | 0 | 1 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 45 | 7 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 59 | 16 | 5 | 0 |
| TREND_PULLBACK_EMA | 5 | 2 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 49 | 8 | 0 | 18.3 | 16.3 | +0.03 | **TUNE** — marginal: avg +0.03R/kill across 57 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 0 | 0 | 1 | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** — only 1 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 78 | 15 | 3 | 50.1 | 24.9 | +0.26 | **KEEP** — net-helping: avg +0.26R/kill across 96 kills (saved 50.1R vs missed 24.9R) |
| regime_shift | 8 | 0 | 1 | 4.9 | 0.0 | +0.55 | **INSUFFICIENT_SAMPLE** — only 9 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 29 | 8 | 6 | 25.5 | 11.9 | +0.32 | **KEEP** — net-helping: avg +0.32R/kill across 43 kills (saved 25.5R vs missed 11.9R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3630931`
- `Path funnel` emissions: `112`
- `Regime distribution` emissions: `112`
- `QUIET_SCALP_BLOCK` events: `312`
- `confidence_gate` events: `16191`
- `free_channel_post` events: `142`
- `pre_tp_fire` events: `66`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **66**
- Avg resolved threshold: **0.488%** raw → avg net **+4.18%** @ 10x
- Avg time-to-fire from dispatch: **290s**
- By threshold source: stamped=66

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 32 | 0.507% | +4.37% | 272 | stamped=32 |
| LIQUIDITY_SWEEP_REVERSAL | 14 | 0.532% | +4.62% | 368 | stamped=14 |
| DIVERGENCE_CONTINUATION | 12 | 0.500% | +4.30% | 241 | stamped=12 |
| FAILED_AUCTION_RECLAIM | 3 | 0.347% | +2.77% | 113 | stamped=3 |
| QUIET_COMPRESSION_BREAK | 3 | 0.200% | +1.30% | 640 | stamped=3 |
| TREND_PULLBACK_EMA | 2 | 0.446% | +3.76% | 80 | stamped=2 |
- Top symbols: 1000PEPEUSDT=9, WIFUSDT=8, OPUSDT=8, FILUSDT=6, XPLUSDT=5, AVGOUSDT=5, QQQUSDT=4, APTUSDT=3, HOMEUSDT=3, HEIUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 2595 | 2595 | 2595 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **142**

| Source | Count |
|---|---:|
| signal_close | 72 |
| pre_tp | 66 |
| regime_shift | 3 |
| signal_highlight | 1 |

- By severity: HIGH=142

## Dependency readiness
- cvd: presence[present=626836] state[populated=626836] buckets[few=29, many=626570, some=237] sources[none] quality[none]
- funding_rate: presence[absent=16383, present=610453] state[empty=16383, populated=610453] buckets[few=610453, none=16383] sources[none] quality[none]
- liquidation_clusters: presence[absent=222073, present=404763] state[empty=222073, populated=404763] buckets[few=258266, none=222073, some=146497] sources[none] quality[none]
- oi_snapshot: presence[absent=13748, present=613088] state[empty=13748, populated=613088] buckets[few=352, many=610917, none=13748, some=1819] sources[none] quality[none]
- order_book: presence[absent=155278, present=471558] state[populated=471558, unavailable=155278] buckets[few=471558, none=155278] sources[book_ticker=471558, unavailable=155278] quality[none=155278, top_of_book_only=471558]
- orderblocks: presence[absent=626836] state[empty=626836] buckets[none=626836] sources[not_implemented=626836] quality[none]
- recent_ticks: presence[absent=8777, present=618059] state[empty=8777, populated=618059] buckets[many=618059, none=8777] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `10.271302580833435` sec
- Median create→first breach: `417.81908905506134` sec
- Median create→terminal: `357.1642179489136` sec
- Median first breach→terminal: `2.06448495388031` sec
- Fast-failure buckets: `{"under_120s": {"count": 14, "pct": 19.4}, "under_180s": {"count": 16, "pct": 22.2}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 10, "pct": 13.9}}`
- ~3 minute terminal-close behavior: `{"count": 8, "pct": 7.1}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 6 | 6 | 0.0 | 33.3 | 0.0 | 0.0 | 0.3347 | 880.9761290550232 | 888.1085119247437 |
| DIVERGENCE_CONTINUATION | 25 | 25 | 0.0 | 8.0 | 0.0 | 48.0 | 0.0161 | 455.1871237754822 | 239.15887594223022 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 0.0 | 0.0 | 0.0 | 50.0 | 0.2879 | 1168.1404775381088 | 970.855672955513 |
| LIQUIDITY_SWEEP_REVERSAL | 25 | 25 | 0.0 | 8.0 | 0.0 | 56.0 | 0.0376 | 264.51694893836975 | 341.0863324403763 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 0.0 | 0.0 | 100.0 | 0.1507 | 1777.6288175582886 | 2319.099790096283 |
| SR_FLIP_RETEST | 46 | 46 | 0.0 | 2.2 | 0.0 | 69.6 | 0.1493 | 348.9636130332947 | 302.1261489391327 |
| TREND_PULLBACK_EMA | 4 | 4 | 0.0 | 25.0 | 0.0 | 50.0 | -0.1633 | 518.0966801643372 | 681.2678334712982 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 26671 | 252 | 11010 | 0.0 | 2.2 | 348.9636130332947 | 302.1261489391327 | 15661 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4587 | 6 | 4306 | 0.0 | 25.0 | 518.0966801643372 | 681.2678334712982 | 281 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `158`
- Gating Δ: `51404`
- No-generation Δ: `852279`
- Fast failures Δ: `-1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 0.6545, "current_avg_pnl": 0.3347, "current_win_rate": 0.0, "previous_avg_pnl": -0.3198, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0665, "current_avg_pnl": 0.0161, "current_win_rate": 0.0, "previous_avg_pnl": -0.0504, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1216, "current_avg_pnl": 0.2879, "current_win_rate": 0.0, "previous_avg_pnl": 0.4095, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.2509, "current_avg_pnl": 0.0376, "current_win_rate": 0.0, "previous_avg_pnl": -0.2133, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.4506, "current_avg_pnl": 0.1507, "current_win_rate": 0.0, "previous_avg_pnl": -0.2999, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.2374, "current_avg_pnl": 0.1493, "current_win_rate": 0.0, "previous_avg_pnl": -0.0881, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.0567, "current_avg_pnl": -0.1633, "current_win_rate": 0.0, "previous_avg_pnl": -0.1066, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": 2750, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -51.61, "median_terminal_delta_sec": -51.19, "sl_rate_delta": -13.2, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 192, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 518.1, "median_terminal_delta_sec": -192.11, "sl_rate_delta": 25.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
