# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `21` sec (warning=False)
- Latest performance record age: `632` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1183 | 1183 | 1124 | 4 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 14433 | 14433 | 13962 | 27 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 308669 | 307486 | 1183 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 285889 | 285889 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 285889 | 271456 | 14433 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 285889 | 275896 | 9993 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 308669 | 308212 | 457 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 308669 | 308660 | 9 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 285889 | 285854 | 35 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 308669 | 308669 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 285889 | 285826 | 63 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 285889 | 285792 | 97 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 285889 | 259388 | 26501 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 285889 | 266831 | 19058 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 285889 | 284123 | 1766 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 308669 | 306940 | 1729 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 308669 | 308669 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 9993 | 9993 | 6620 | 58 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 457 | 457 | 379 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 9 | 9 | 9 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 19058 | 19058 | 14406 | 164 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 35 | 35 | 24 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 63 | 63 | 19 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 97 | 97 | 96 | 1 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 26501 | 26501 | 11617 | 235 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1766 | 1766 | 1689 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1729 | 1729 | 1698 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=307486): breakout_not_found=171471, basic_filters_failed=98272, retest_proximity_failed=30334, volume_spike_missing=5097, ema_alignment_reject=1927, missing_fvg_or_orderblock=385
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=285889): cls_disabled_merged_into_lsr=285889
- **EVAL::DIVERGENCE_CONTINUATION** (total=271456): basic_filters_failed=89718, cvd_divergence_failed=84054, h1_trend_not_aligned=62935, ema_alignment_reject=25506, regime_blocked=5057, retest_proximity_failed=2688, missing_fvg_or_orderblock=1498
- **EVAL::FAILED_AUCTION_RECLAIM** (total=275896): auction_not_detected=101600, basic_filters_failed=89718, reclaim_hold_failed=48876, tail_too_small=35702
- **EVAL::FUNDING_EXTREME** (total=308212): funding_not_extreme=198884, basic_filters_failed=95885, missing_funding_rate=7520, ema_alignment_reject=3426, rsi_reject=1611, cvd_divergence_failed=425, momentum_reject=404, missing_fvg_or_orderblock=57
- **EVAL::LIQUIDATION_REVERSAL** (total=308660): cascade_threshold_not_met=207761, basic_filters_failed=98272, cvd_divergence_failed=1486, rsi_reject=1026, missing_fvg_or_orderblock=98, volume_spike_missing=17
- **EVAL::MA_CROSS_TREND_SHIFT** (total=285854): no_ma_cross=188284, basic_filters_failed=89718, ma_cross_cooldown=7852
- **EVAL::OPENING_RANGE_BREAKOUT** (total=308669): feature_disabled=308669
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=285826): regime_blocked=215719, breakout_not_found=33574, basic_filters_failed=13663, ema_alignment_reject=13360, adx_reject=9510
- **EVAL::QUIET_COMPRESSION_BREAK** (total=285792): compression_not_detected=135790, basic_filters_failed=76055, regime_blocked=70170, breakout_not_detected=3397, volume_confirmation_failed=238, rsi_reject=142
- **EVAL::SR_FLIP_RETEST** (total=259388): basic_filters_failed=89718, reclaim_hold_failed=62219, flip_close_not_confirmed=45785, retest_out_of_zone=44271, wick_quality_failed=11661, ema_alignment_reject=2956, missing_fvg_or_orderblock=2601, rsi_reject=177
- **EVAL::STANDARD** (total=266831): momentum_reject=70406, adx_reject=62882, basic_filters_failed=62164, macd_reject=30499, sweeps_not_detected=24944, ema_alignment_reject=12956, invalid_sl_geometry=2403, rsi_reject=577
- **EVAL::TREND_PULLBACK** (total=284123): h1_trend_not_aligned=96235, ema_alignment_reject=45832, basic_filters_failed=45797, h1_pullback_not_confirmed=22026, no_ema_reclaim_close=17909, body_conviction_fail=14070, ema_not_tested_prev=12867, rsi_reject=11054, regime_blocked=9294, prev_already_below_emas=3608, prev_already_above_emas=2354, no_prev_low_break=1395, no_prev_high_break=870, momentum_flat=373, momentum_reject=179, ema21_not_tagged=146, missing_fvg_or_orderblock=114
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=306940): breakout_not_found=158046, basic_filters_failed=98272, retest_proximity_failed=39049, volume_spike_missing=8045, ema_alignment_reject=2247, missing_fvg_or_orderblock=1256, rsi_reject=25
- **EVAL::WHALE_MOMENTUM** (total=308669): momentum_reject=219020, recent_ticks_insufficient=65310, basic_filters_failed=24339

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 271887 | 71.3% |
| TRENDING_UP | 49020 | 12.9% |
| TRENDING_DOWN | 43796 | 11.5% |
| RANGING | 16542 | 4.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1473**
- Average confidence gap to threshold: **16.67** (samples=1473) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: EDENUSDT=66, MUUSDT=56, TRXUSDT=48, BZUSDT=45, BEATUSDT=43, AAVEUSDT=42, VIRTUALUSDT=40, PENGUUSDT=39, DOGEUSDT=39, BNBUSDT=36

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 6 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 106 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 222 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 297 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 169 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 658 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 562 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 910 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 21 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 23 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| RANGE_FADE | filtered | quiet_scalp_min_confidence | 1 |
| RANGE_FADE | kept | min_confidence_pass | 3 |
| SR_FLIP_RETEST | filtered | min_confidence | 1548 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 613 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2048 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 46 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 6 | 55.78 | 65.00 | 9.22 | 20.78 | 20.00 | 15.85 | 0.00 | 9.92 |
| BREAKDOWN_SHORT | kept | 8 | 68.36 | 65.00 | -3.36 | 20.80 | 19.69 | 17.82 | 0.00 | 3.16 |
| DIVERGENCE_CONTINUATION | filtered | 106 | 55.47 | 65.00 | 9.53 | 19.98 | 19.85 | 18.32 | 2.79 | 12.71 |
| DIVERGENCE_CONTINUATION | kept | 222 | 71.59 | 65.00 | -6.59 | 20.34 | 19.85 | 17.36 | 2.58 | -0.44 |
| FAILED_AUCTION_RECLAIM | filtered | 466 | 50.87 | 65.00 | 14.13 | 20.57 | 19.44 | 20.00 | 4.13 | 11.91 |
| FAILED_AUCTION_RECLAIM | kept | 658 | 69.56 | 65.00 | -4.56 | 21.21 | 19.78 | 20.00 | 4.76 | 0.68 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 66.50 | 65.00 | -1.50 | 20.90 | 19.45 | 17.00 | 2.00 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 654 | 48.11 | 65.00 | 16.89 | 20.77 | 19.60 | 15.20 | 2.44 | 14.64 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 910 | 68.90 | 65.00 | -3.90 | 21.59 | 19.60 | 15.20 | 2.10 | 0.33 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 21 | 61.00 | 65.00 | 4.00 | 20.39 | 20.00 | 20.00 | 1.50 | 6.00 |
| POST_DISPLACEMENT_CONTINUATION | kept | 23 | 82.96 | 65.00 | -17.96 | 22.12 | 20.00 | 19.97 | 5.61 | 6.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 67.40 | 65.00 | -2.40 | 18.00 | 20.00 | 20.00 | 0.00 | 4.30 |
| RANGE_FADE | filtered | 1 | 51.40 | 65.00 | 13.60 | 21.20 | 20.00 | 13.40 | 0.00 | 14.40 |
| RANGE_FADE | kept | 3 | 68.03 | 65.00 | -3.03 | 20.27 | 19.73 | 13.40 | 0.00 | 0.30 |
| SR_FLIP_RETEST | filtered | 2161 | 53.83 | 65.00 | 11.17 | 20.55 | 19.91 | 15.85 | 1.78 | 11.12 |
| SR_FLIP_RETEST | kept | 2048 | 69.72 | 65.00 | -4.72 | 20.89 | 19.98 | 15.80 | 2.15 | 0.36 |
| TREND_PULLBACK_EMA | filtered | 3 | 56.30 | 65.00 | 8.70 | 20.53 | 19.87 | 15.80 | 4.83 | 1.87 |
| TREND_PULLBACK_EMA | kept | 46 | 76.07 | 65.00 | -11.07 | 19.83 | 19.40 | 18.62 | 4.52 | 0.48 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 63.50 | 65.00 | 1.50 | 24.20 | 19.00 | 20.00 | 1.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 76.51 | 65.00 | -11.51 | 20.57 | 18.69 | 20.00 | 4.36 | 1.29 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 6 | 55.78 | 16.67 | 18.00 | 3.00 | 14.00 | 4.58 | 9.45 | 0.00 |
| BREAKDOWN_SHORT | kept | 8 | 68.36 | 23.00 | 16.75 | 6.38 | 12.62 | 5.06 | 7.71 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 106 | 55.47 | 20.62 | 18.00 | 4.10 | 11.77 | 5.48 | 6.92 | 2.79 |
| DIVERGENCE_CONTINUATION | kept | 222 | 71.59 | 21.54 | 18.00 | 4.74 | 11.92 | 5.98 | 8.01 | 2.58 |
| FAILED_AUCTION_RECLAIM | filtered | 466 | 50.87 | 21.12 | 14.30 | 6.77 | 11.13 | 6.38 | 5.22 | 4.13 |
| FAILED_AUCTION_RECLAIM | kept | 658 | 69.56 | 23.72 | 14.24 | 4.19 | 10.88 | 6.51 | 6.01 | 4.76 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 66.50 | 21.00 | 8.00 | 6.00 | 15.50 | 6.50 | 10.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 654 | 48.11 | 21.75 | 14.10 | 7.36 | 12.63 | 5.59 | 5.54 | 2.44 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 910 | 68.90 | 23.95 | 14.32 | 4.42 | 12.52 | 5.86 | 6.10 | 2.10 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 21 | 61.00 | 17.00 | 18.00 | 3.00 | 11.00 | 8.50 | 8.00 | 1.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 23 | 82.96 | 22.91 | 18.00 | 12.00 | 13.87 | 8.57 | 8.00 | 5.61 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 67.40 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 2.70 | 0.00 |
| RANGE_FADE | filtered | 1 | 51.40 | 25.00 | 18.00 | 3.00 | 10.00 | 2.50 | 7.30 | 0.00 |
| RANGE_FADE | kept | 3 | 68.03 | 25.00 | 18.00 | 4.00 | 11.33 | 3.33 | 6.63 | 0.00 |
| SR_FLIP_RETEST | filtered | 2161 | 53.83 | 20.35 | 15.16 | 6.03 | 12.91 | 6.84 | 5.84 | 1.78 |
| SR_FLIP_RETEST | kept | 2048 | 69.72 | 21.86 | 15.16 | 5.02 | 13.51 | 6.19 | 7.48 | 2.15 |
| TREND_PULLBACK_EMA | filtered | 3 | 56.30 | 19.67 | 18.00 | 3.00 | 14.00 | 8.33 | 5.33 | 4.83 |
| TREND_PULLBACK_EMA | kept | 46 | 76.07 | 20.48 | 18.00 | 3.26 | 13.91 | 7.95 | 8.96 | 4.52 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 63.50 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.00 | 1.50 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 76.51 | 23.86 | 18.00 | 7.71 | 11.14 | 5.86 | 6.87 | 4.36 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 6 | 55.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 8 | 68.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.90 | 0.00 | 0.00 | **0.90** |
| DIVERGENCE_CONTINUATION | filtered | 106 | 55.47 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | **0.14** |
| DIVERGENCE_CONTINUATION | kept | 222 | 71.59 | 0.00 | 0.00 | 0.82 | 0.00 | 0.00 | 0.00 | 0.00 | **0.82** |
| FAILED_AUCTION_RECLAIM | filtered | 466 | 50.87 | 0.00 | 0.00 | 1.54 | 0.00 | 6.29 | 0.00 | 0.00 | **7.83** |
| FAILED_AUCTION_RECLAIM | kept | 658 | 69.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | **0.07** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 66.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 654 | 48.11 | 0.00 | 0.00 | 2.44 | 0.00 | 9.81 | 0.00 | 0.00 | **12.25** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 910 | 68.90 | 0.00 | 0.00 | 0.01 | 0.00 | 0.04 | 0.00 | 0.00 | **0.05** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 21 | 61.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| POST_DISPLACEMENT_CONTINUATION | kept | 23 | 82.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 67.40 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | **4.30** |
| RANGE_FADE | filtered | 1 | 51.40 | 0.00 | 0.00 | 14.40 | 0.00 | 0.00 | 0.00 | 0.00 | **14.40** |
| RANGE_FADE | kept | 3 | 68.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 2161 | 53.83 | 0.00 | 0.00 | 0.27 | 0.00 | 4.53 | 0.00 | 0.00 | **4.80** |
| SR_FLIP_RETEST | kept | 2048 | 69.72 | 0.00 | 0.00 | 0.05 | 0.00 | 0.34 | 0.00 | 0.00 | **0.39** |
| TREND_PULLBACK_EMA | filtered | 3 | 56.30 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| TREND_PULLBACK_EMA | kept | 46 | 76.07 | 0.00 | 0.00 | 2.50 | 0.00 | 0.00 | 0.00 | 0.00 | **2.50** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 63.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 76.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=307 (69.1%) | PREMATURE=39 (8.8%) | NEUTRAL=98 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=3
- **Net-helping** — invalidation saved on 268 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 6 | 2 | 0 | 0 |
| ema_crossover | 11 | 0 | 1 | 0 |
| momentum_loss | 207 | 22 | 48 | 0 |
| regime_shift | 83 | 15 | 49 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 6 | 0 | 2 | 0 |
| DIVERGENCE_CONTINUATION | 22 | 1 | 4 | 0 |
| FAILED_AUCTION_RECLAIM | 56 | 4 | 14 | 0 |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 84 | 16 | 47 | 0 |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1 | 0 |
| RANGE_FADE | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 129 | 17 | 29 | 0 |
| TREND_PULLBACK_EMA | 6 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 1 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 6 | 2 | 0 | 1.6 | 4.5 | -0.36 | **INSUFFICIENT_SAMPLE** — only 8 classified kills (need >= 20); let data accumulate before tuning |
| ema_crossover | 11 | 0 | 1 | 5.7 | 0.0 | +0.48 | **INSUFFICIENT_SAMPLE** — only 12 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 207 | 22 | 48 | 116.8 | 33.6 | +0.30 | **KEEP** — net-helping: avg +0.30R/kill across 277 kills (saved 116.8R vs missed 33.6R) |
| regime_shift | 83 | 15 | 49 | 48.0 | 19.9 | +0.19 | **KEEP** — net-helping: avg +0.19R/kill across 147 kills (saved 48.0R vs missed 19.9R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1973888`
- `Path funnel` emissions: `53`
- `Regime distribution` emissions: `53`
- `QUIET_SCALP_BLOCK` events: `1473`
- `confidence_gate` events: `7347`
- `free_channel_post` events: `200`
- `pre_tp_fire` events: `90`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **90**
- Avg resolved threshold: **0.413%** raw → avg net **+3.43%** @ 10x
- Avg time-to-fire from dispatch: **378s**
- By threshold source: stamped=90

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 33 | 0.337% | +2.67% | 487 | stamped=33 |
| LIQUIDITY_SWEEP_REVERSAL | 32 | 0.487% | +4.17% | 319 | stamped=32 |
| FAILED_AUCTION_RECLAIM | 14 | 0.394% | +3.24% | 328 | stamped=14 |
| DIVERGENCE_CONTINUATION | 10 | 0.409% | +3.39% | 295 | stamped=10 |
| TREND_PULLBACK_EMA | 1 | 0.902% | +8.32% | 175 | stamped=1 |
- Top symbols: FETUSDT=7, PLAYUSDT=6, NILUSDT=6, FARTCOINUSDT=5, BLUAIUSDT=5, MYXUSDT=4, PLUMEUSDT=4, HANAUSDT=4, SOLUSDT=4, GENIUSUSDT=4

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 4 | 17408 | 25369 | 27070 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **200**

| Source | Count |
|---|---:|
| signal_close | 103 |
| pre_tp | 90 |
| regime_shift | 6 |
| signal_highlight | 1 |

- By severity: HIGH=200

## Dependency readiness
- cvd: presence[present=308669] state[populated=308669] buckets[many=308669] sources[none] quality[none]
- funding_rate: presence[absent=7520, present=301149] state[empty=7520, populated=301149] buckets[few=301149, none=7520] sources[none] quality[none]
- liquidation_clusters: presence[absent=181123, present=127546] state[empty=181123, populated=127546] buckets[few=96465, none=181123, some=31081] sources[none] quality[none]
- oi_snapshot: presence[absent=2932, present=305737] state[empty=2932, populated=305737] buckets[many=305737, none=2932] sources[none] quality[none]
- order_book: presence[absent=78239, present=230430] state[populated=230430, unavailable=78239] buckets[few=230430, none=78239] sources[book_ticker=230430, unavailable=78239] quality[none=78239, top_of_book_only=230430]
- orderblocks: presence[absent=308669] state[empty=308669] buckets[none=308669] sources[not_implemented=308669] quality[none]
- recent_ticks: presence[present=308669] state[populated=308669] buckets[many=308669] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.760487914085388` sec
- Median create→first breach: `582.9443370103836` sec
- Median create→terminal: `712.7869555950165` sec
- Median first breach→terminal: `11.444432377815247` sec
- Fast-failure buckets: `{"under_120s": {"count": 11, "pct": 10.8}, "under_180s": {"count": 17, "pct": 16.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 3, "pct": 2.9}}`
- ~3 minute terminal-close behavior: `{"count": 9, "pct": 5.8}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.4805 | 579.8278809785843 | 593.5396249294281 |
| DIVERGENCE_CONTINUATION | 17 | 17 | 0.0 | 23.5 | 0.0 | 58.8 | -0.108 | 553.1314039230347 | 666.4600188732147 |
| FAILED_AUCTION_RECLAIM | 22 | 22 | 0.0 | 4.5 | 0.0 | 63.6 | 0.0595 | 987.1209275722504 | 969.284735918045 |
| LIQUIDITY_SWEEP_REVERSAL | 52 | 52 | 0.0 | 19.2 | 0.0 | 61.5 | -0.0794 | 486.3184210062027 | 622.5428780317307 |
| RANGE_FADE | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -3.1587 | None | 607.5967648029327 |
| SR_FLIP_RETEST | 58 | 58 | 0.0 | 10.3 | 0.0 | 56.9 | 0.0017 | 632.5761399269104 | 741.762589931488 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 50.0 | -0.0196 | 772.2345650196075 | 736.8203248977661 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 26501 | 235 | 11617 | 0.0 | 10.3 | 632.5761399269104 | 741.762589931488 | 14884 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1766 | 9 | 1689 | 0.0 | 0.0 | 772.2345650196075 | 736.8203248977661 | 77 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-57`
- Gating Δ: `-2906`
- No-generation Δ: `-884232`
- Fast failures Δ: `-5`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.4805, "current_avg_pnl": -0.4805, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.2378, "current_avg_pnl": -0.108, "current_win_rate": 0.0, "previous_avg_pnl": 0.1298, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0517, "current_avg_pnl": 0.0595, "current_win_rate": 0.0, "previous_avg_pnl": 0.0078, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.1312, "current_avg_pnl": -0.0794, "current_win_rate": 0.0, "previous_avg_pnl": -0.2106, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0114, "current_avg_pnl": 0.0017, "current_win_rate": 0.0, "previous_avg_pnl": -0.0097, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.4281, "current_avg_pnl": -0.0196, "current_win_rate": 0.0, "previous_avg_pnl": -0.4477, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 30, "geometry_changed_delta": 0, "geometry_preserved_delta": 2192, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 131.49, "median_terminal_delta_sec": 53.02, "sl_rate_delta": -3.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 347.92, "median_terminal_delta_sec": 201.17, "sl_rate_delta": -33.3, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **MA_CROSS_TREND_SHIFT**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
