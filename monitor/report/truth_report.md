# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `648` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 718 | 718 | 543 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 22428 | 22428 | 19254 | 28 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 180659 | 180467 | 225 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 153746 | 153762 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 153158 | 146618 | 7110 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 153811 | 149450 | 4607 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 181902 | 181036 | 947 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 180568 | 180578 | 6 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 154069 | 154133 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 180697 | 180706 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 153767 | 153783 | 24 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 153136 | 153072 | 84 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 151868 | 142645 | 10400 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 151048 | 138135 | 13568 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 151707 | 151539 | 211 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 180606 | 179966 | 687 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 180586 | 180598 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 16057 | 16057 | 12590 | 63 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 4438 | 4438 | 4367 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 39 | 39 | 39 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 61745 | 61745 | 53735 | 122 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 7 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 128 | 128 | 128 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 176 | 176 | 141 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 45868 | 45868 | 31139 | 129 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 687 | 687 | 668 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2805 | 2805 | 1933 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=180468): breakout_not_found=113946, basic_filters_failed=36191, retest_proximity_failed=21683, ema_alignment_reject=5460, volume_spike_missing=2791, insufficient_candles=229, missing_fvg_or_orderblock=119, rsi_reject=49
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=153763): cls_disabled_merged_into_lsr=153763
- **EVAL::DIVERGENCE_CONTINUATION** (total=146619): cvd_divergence_failed=59103, basic_filters_failed=30198, h1_trend_not_aligned=26110, ema_alignment_reject=19885, retest_proximity_failed=10003, regime_blocked=770, missing_fvg_or_orderblock=550
- **EVAL::FAILED_AUCTION_RECLAIM** (total=149451): auction_not_detected=58456, reclaim_hold_failed=31074, basic_filters_failed=27395, tail_too_small=22602, regime_blocked=9924
- **EVAL::FUNDING_EXTREME** (total=181037): funding_not_extreme=133485, basic_filters_failed=34586, ema_alignment_reject=6260, missing_funding_rate=3988, momentum_reject=1113, rsi_reject=813, cvd_divergence_failed=745, missing_fvg_or_orderblock=47
- **EVAL::LIQUIDATION_REVERSAL** (total=180579): cascade_threshold_not_met=140893, basic_filters_failed=36190, cvd_divergence_failed=1870, rsi_reject=1370, insufficient_candles=143, missing_fvg_or_orderblock=75, volume_spike_missing=38
- **EVAL::MA_CROSS_TREND_SHIFT** (total=154134): no_ma_cross=122473, basic_filters_failed=30204, ma_cross_cooldown=1457
- **EVAL::OPENING_RANGE_BREAKOUT** (total=180707): feature_disabled=180707
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=153784): regime_blocked=84330, breakout_not_found=53476, basic_filters_failed=12215, adx_reject=3732, ema_alignment_reject=26, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=153073): regime_blocked=79034, compression_not_detected=54553, basic_filters_failed=15178, breakout_not_detected=4016, volume_confirmation_failed=247, rsi_reject=45
- **EVAL::SR_FLIP_RETEST** (total=142646): retest_out_of_zone=39850, reclaim_hold_failed=27885, basic_filters_failed=27390, flip_close_not_confirmed=27375, regime_blocked=9883, ema_alignment_reject=5192, wick_quality_failed=4572, missing_fvg_or_orderblock=465, rsi_reject=34
- **EVAL::STANDARD** (total=138135): momentum_reject=52938, basic_filters_failed=23480, ema_alignment_reject=17162, adx_reject=14109, sweeps_not_detected=13519, macd_reject=12599, invalid_sl_geometry=3429, rsi_reject=896, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=151540): ema_alignment_reject=38329, h1_pullback_not_confirmed=36209, h1_trend_not_aligned=31008, basic_filters_failed=16425, ema_not_tested_prev=16051, no_ema_reclaim_close=7361, rsi_reject=2374, body_conviction_fail=1538, regime_blocked=1108, prev_already_above_emas=335, prev_already_below_emas=322, no_prev_low_break=185, no_prev_high_break=143, momentum_flat=62, ema21_not_tagged=43, momentum_reject=41, missing_fvg_or_orderblock=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=179967): breakout_not_found=108524, basic_filters_failed=36191, retest_proximity_failed=27268, volume_spike_missing=5706, ema_alignment_reject=1695, missing_fvg_or_orderblock=345, insufficient_candles=229, rsi_reject=9
- **EVAL::WHALE_MOMENTUM** (total=180599): momentum_reject=159932, recent_ticks_insufficient=15860, basic_filters_failed=4807

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 408530 | 42.1% |
| TRENDING_UP | 284235 | 29.3% |
| TRENDING_DOWN | 118189 | 12.2% |
| QUIET | 84416 | 8.7% |
| VOLATILE | 76103 | 7.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **246**
- Average confidence gap to threshold: **15.15** (samples=246) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BZUSDT=123, SPYUSDT=43, TRXUSDT=42, UNIUSDT=11, BTCUSDT=10, BNBUSDT=9, QQQUSDT=4, WLFIUSDT=3, MSTRUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 23 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 230 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 709 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 458 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 73 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1345 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1343 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 29 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1795 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 2 |
| SR_FLIP_RETEST | filtered | min_confidence | 3147 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 122 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2256 |
| TREND_PULLBACK_CONTINUATION | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 10 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 111 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 23 | 54.34 | 65.00 | 10.66 | 19.83 | 20.00 | 20.00 | 0.00 | 11.91 |
| BREAKDOWN_SHORT | kept | 1 | 67.50 | 65.00 | -2.50 | 20.50 | 20.00 | 20.00 | 0.00 | 7.80 |
| DIVERGENCE_CONTINUATION | filtered | 230 | 56.67 | 65.00 | 8.33 | 20.80 | 19.20 | 18.25 | 2.90 | 11.47 |
| DIVERGENCE_CONTINUATION | kept | 709 | 70.02 | 65.00 | -5.02 | 19.69 | 19.28 | 18.35 | 2.42 | -2.17 |
| FAILED_AUCTION_RECLAIM | filtered | 531 | 52.99 | 65.00 | 12.01 | 20.64 | 19.47 | 20.00 | 2.91 | 8.91 |
| FAILED_AUCTION_RECLAIM | kept | 1345 | 73.34 | 65.00 | -8.34 | 20.55 | 19.66 | 20.00 | 4.37 | 0.23 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1372 | 55.68 | 65.00 | 9.32 | 20.11 | 19.70 | 18.43 | 1.92 | 6.51 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1795 | 70.93 | 65.00 | -5.93 | 20.77 | 19.85 | 17.84 | 3.15 | 0.56 |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 52.25 | 65.00 | 12.75 | 20.32 | 20.00 | 20.00 | 0.00 | 7.50 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 80.10 | 65.00 | -15.10 | 22.50 | 20.00 | 20.00 | 0.00 | -1.50 |
| SR_FLIP_RETEST | filtered | 3269 | 53.91 | 65.00 | 11.09 | 19.91 | 19.84 | 15.95 | 1.79 | 8.09 |
| SR_FLIP_RETEST | kept | 2256 | 71.19 | 65.00 | -6.19 | 20.73 | 19.89 | 15.84 | 1.92 | 0.65 |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 59.30 | 65.00 | 5.70 | 20.70 | 20.00 | 16.40 | 0.00 | 9.00 |
| TREND_PULLBACK_EMA | filtered | 5 | 59.30 | 65.00 | 5.70 | 20.20 | 19.60 | 20.00 | 4.00 | 9.00 |
| TREND_PULLBACK_EMA | kept | 10 | 72.55 | 65.00 | -7.55 | 20.78 | 19.96 | 18.19 | 5.55 | -2.70 |
| VOLUME_SURGE_BREAKOUT | filtered | 111 | 55.85 | 65.00 | 9.15 | 20.25 | 19.42 | 20.00 | 3.33 | 7.00 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 66.80 | 65.00 | -1.80 | 18.40 | 20.00 | 20.00 | 4.50 | 3.00 |
| WHALE_MOMENTUM | kept | 1 | 65.00 | 65.00 | 0.00 | 20.70 | 20.00 | 17.00 | 0.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 23 | 54.34 | 17.52 | 18.00 | 3.00 | 13.65 | 4.78 | 9.30 | 0.00 |
| BREAKDOWN_SHORT | kept | 1 | 67.50 | 25.00 | 18.00 | 3.00 | 14.00 | 8.00 | 7.30 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 230 | 56.67 | 22.08 | 10.83 | 5.86 | 11.68 | 6.68 | 8.13 | 2.90 |
| DIVERGENCE_CONTINUATION | kept | 709 | 70.02 | 20.10 | 17.63 | 4.45 | 11.53 | 5.23 | 8.84 | 2.42 |
| FAILED_AUCTION_RECLAIM | filtered | 531 | 52.99 | 21.74 | 16.89 | 4.57 | 12.49 | 6.44 | 5.58 | 2.91 |
| FAILED_AUCTION_RECLAIM | kept | 1345 | 73.34 | 22.43 | 15.86 | 4.41 | 11.82 | 6.25 | 8.46 | 4.37 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1372 | 55.68 | 22.21 | 14.01 | 7.27 | 13.26 | 5.38 | 5.44 | 1.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1795 | 70.93 | 21.79 | 14.04 | 4.99 | 13.01 | 5.82 | 8.69 | 3.15 |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 52.25 | 18.82 | 18.00 | 10.36 | 14.00 | 5.80 | 4.36 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 80.10 | 17.00 | 18.00 | 13.50 | 15.50 | 6.75 | 9.35 | 0.00 |
| SR_FLIP_RETEST | filtered | 3269 | 53.91 | 20.40 | 17.63 | 4.50 | 12.62 | 6.05 | 6.25 | 1.79 |
| SR_FLIP_RETEST | kept | 2256 | 71.19 | 20.68 | 17.51 | 4.59 | 12.90 | 6.01 | 9.34 | 1.92 |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 59.30 | 25.00 | 8.00 | 3.00 | 14.00 | 9.00 | 9.30 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 5 | 59.30 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 7.30 | 4.00 |
| TREND_PULLBACK_EMA | kept | 10 | 72.55 | 17.00 | 18.00 | 3.30 | 14.00 | 5.00 | 9.70 | 5.55 |
| VOLUME_SURGE_BREAKOUT | filtered | 111 | 55.85 | 25.00 | 11.87 | 8.62 | 10.04 | 5.00 | 4.80 | 3.33 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 66.80 | 25.00 | 8.00 | 12.00 | 10.00 | 5.00 | 5.30 | 4.50 |
| WHALE_MOMENTUM | kept | 1 | 65.00 | 17.00 | 18.00 | 3.00 | 11.00 | 8.00 | 8.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 23 | 54.34 | 8.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.22** |
| BREAKDOWN_SHORT | kept | 1 | 67.50 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| DIVERGENCE_CONTINUATION | filtered | 230 | 56.67 | 0.23 | 0.00 | 1.38 | 0.00 | 2.85 | 0.36 | 0.00 | 0.00 | **4.82** |
| DIVERGENCE_CONTINUATION | kept | 709 | 70.02 | 0.00 | 0.00 | 0.02 | 0.00 | 0.19 | 0.04 | 0.00 | 0.00 | **0.25** |
| FAILED_AUCTION_RECLAIM | filtered | 531 | 52.99 | 0.00 | 0.00 | 3.49 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | **3.99** |
| FAILED_AUCTION_RECLAIM | kept | 1345 | 73.34 | 0.00 | 0.00 | 0.16 | 0.00 | 0.01 | 0.01 | 0.00 | 0.00 | **0.18** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1372 | 55.68 | 0.05 | 0.00 | 1.88 | 0.00 | 4.18 | 0.11 | 0.00 | 0.00 | **6.22** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1795 | 70.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 0.00 | **0.46** |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 52.25 | 0.00 | 0.00 | 3.27 | 0.00 | 0.00 | 0.00 | 0.00 | 4.91 | **8.18** |
| QUIET_COMPRESSION_BREAK | kept | 2 | 80.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 3269 | 53.91 | 0.11 | 0.00 | 0.19 | 0.00 | 0.67 | 0.04 | 0.00 | 1.16 | **2.17** |
| SR_FLIP_RETEST | kept | 2256 | 71.19 | 0.00 | 0.00 | 0.03 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **0.22** |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 59.30 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| TREND_PULLBACK_EMA | filtered | 5 | 59.30 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| TREND_PULLBACK_EMA | kept | 10 | 72.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 111 | 55.85 | 0.00 | 0.00 | 3.39 | 0.00 | 3.05 | 0.00 | 0.00 | 0.00 | **6.44** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 66.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=187 (79.6%) | PREMATURE=34 (14.5%) | NEUTRAL=14 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 153 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 56 | 9 | 0 | 0 |
| ema_crossover | 1 | 1 | 1 | 0 |
| momentum_loss | 91 | 15 | 6 | 0 |
| regime_shift | 8 | 0 | 1 | 0 |
| trailing_invalidation | 31 | 9 | 6 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 9 | 2 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 33 | 4 | 2 | 0 |
| FAILED_AUCTION_RECLAIM | 19 | 0 | 2 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 49 | 8 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 66 | 18 | 5 | 0 |
| TREND_PULLBACK_EMA | 5 | 2 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 56 | 9 | 0 | 21.7 | 18.0 | +0.06 | **TUNE** — marginal: avg +0.06R/kill across 65 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 1 | 1 | 1 | 0.3 | 1.5 | -0.40 | **INSUFFICIENT_SAMPLE** — only 3 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 91 | 15 | 6 | 57.5 | 24.9 | +0.29 | **KEEP** — net-helping: avg +0.29R/kill across 112 kills (saved 57.5R vs missed 24.9R) |
| regime_shift | 8 | 0 | 1 | 4.9 | 0.0 | +0.55 | **INSUFFICIENT_SAMPLE** — only 9 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 31 | 9 | 6 | 27.3 | 13.2 | +0.31 | **KEEP** — net-helping: avg +0.31R/kill across 46 kills (saved 27.3R vs missed 13.2R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4172099`
- `Path funnel` emissions: `134`
- `Regime distribution` emissions: `134`
- `QUIET_SCALP_BLOCK` events: `246`
- `confidence_gate` events: `11684`
- `free_channel_post` events: `109`
- `pre_tp_fire` events: `51`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **51**
- Avg resolved threshold: **0.470%** raw → avg net **+4.00%** @ 10x
- Avg time-to-fire from dispatch: **227s**
- By threshold source: stamped=51

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 26 | 0.435% | +3.65% | 273 | stamped=26 |
| DIVERGENCE_CONTINUATION | 8 | 0.430% | +3.60% | 110 | stamped=8 |
| FAILED_AUCTION_RECLAIM | 8 | 0.491% | +4.21% | 312 | stamped=8 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 0.557% | +4.87% | 113 | stamped=7 |
| TREND_PULLBACK_EMA | 2 | 0.692% | +6.22% | 156 | stamped=2 |
- Top symbols: APTUSDT=8, FILUSDT=6, BABYUSDT=5, 1000PEPEUSDT=4, VELVETUSDT=4, WLFIUSDT=3, OPUSDT=3, EPICUSDT=3, 1000SHIBUSDT=3, 龙虾USDT=3

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **109**

| Source | Count |
|---|---:|
| pre_tp | 51 |
| signal_close | 51 |
| regime_shift | 7 |

- By severity: HIGH=109

## Dependency readiness
- cvd: presence[present=765068] state[populated=765068] buckets[many=764985, some=83] sources[none] quality[none]
- funding_rate: presence[absent=11630, present=753438] state[empty=11630, populated=753438] buckets[few=753438, none=11630] sources[none] quality[none]
- liquidation_clusters: presence[absent=366259, present=398809] state[empty=366259, populated=398809] buckets[few=290884, none=366259, some=107925] sources[none] quality[none]
- oi_snapshot: presence[absent=8269, present=756799] state[empty=8269, populated=756799] buckets[few=289, many=754336, none=8269, some=2174] sources[none] quality[none]
- order_book: presence[absent=193919, present=571149] state[populated=571149, unavailable=193919] buckets[few=571149, none=193919] sources[book_ticker=571149, unavailable=193919] quality[none=193919, top_of_book_only=571149]
- orderblocks: presence[absent=765068] state[empty=765068] buckets[none=765068] sources[not_implemented=765068] quality[none]
- recent_ticks: presence[absent=23223, present=741845] state[empty=23223, populated=741845] buckets[many=741845, none=23223] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.226347088813782` sec
- Median create→first breach: `394.59013390541077` sec
- Median create→terminal: `355.267333984375` sec
- Median first breach→terminal: `1.503105878829956` sec
- Fast-failure buckets: `{"under_120s": {"count": 13, "pct": 25.5}, "under_180s": {"count": 14, "pct": 27.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 10, "pct": 19.6}}`
- ~3 minute terminal-close behavior: `{"count": 7, "pct": 8.8}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 14 | 14 | 0.0 | 0.0 | 0.0 | 57.1 | 0.035 | 82.67965698242188 | 131.9275984764099 |
| FAILED_AUCTION_RECLAIM | 12 | 12 | 0.0 | 8.3 | 0.0 | 66.7 | -0.0376 | 596.1601910591125 | 503.2086389064789 |
| LIQUIDITY_SWEEP_REVERSAL | 13 | 13 | 0.0 | 15.4 | 0.0 | 53.8 | -0.1553 | 297.7060339450836 | 356.4654688835144 |
| SR_FLIP_RETEST | 38 | 38 | 0.0 | 5.3 | 0.0 | 68.4 | 0.0633 | 396.7999144792557 | 406.91052639484406 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 100.0 | 0.346 | 515.7176184654236 | 519.593761920929 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0481 | None | 128.97692704200745 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 45868 | 129 | 31139 | 0.0 | 5.3 | 396.7999144792557 | 406.91052639484406 | 14729 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 687 | 2 | 668 | 0.0 | 0.0 | 515.7176184654236 | 519.593761920929 | 19 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-307`
- Gating Δ: `6731`
- No-generation Δ: `447233`
- Fast failures Δ: `0`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.3347, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.3347, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0264, "current_avg_pnl": 0.035, "current_win_rate": 0.0, "previous_avg_pnl": 0.0086, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.677, "current_avg_pnl": -0.0376, "current_win_rate": 0.0, "previous_avg_pnl": 0.6394, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.1733, "current_avg_pnl": -0.1553, "current_win_rate": 0.0, "previous_avg_pnl": 0.018, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1507, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.1507, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0766, "current_avg_pnl": 0.0633, "current_win_rate": 0.0, "previous_avg_pnl": 0.1399, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.5093, "current_avg_pnl": 0.346, "current_win_rate": 0.0, "previous_avg_pnl": -0.1633, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -118, "geometry_changed_delta": 0, "geometry_preserved_delta": -688, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 74.87, "median_terminal_delta_sec": 128.94, "sl_rate_delta": 2.8, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -340, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2.38, "median_terminal_delta_sec": -161.67, "sl_rate_delta": -25.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
