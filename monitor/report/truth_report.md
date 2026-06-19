# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `465` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 3381 | 3381 | 547 | 41 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 50470 | 50470 | 43659 | 33 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 194189 | 193720 | 520 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 178226 | 178251 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 177410 | 167297 | 10905 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 178307 | 162946 | 15744 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 199326 | 199040 | 344 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 194106 | 194103 | 18 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 178699 | 178761 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_TREND_PULLBACK | 192652 | 179097 | 14351 | 0 | 0 | 0 | low-sample (no_ma_stack) |
| EVAL::OPENING_RANGE_BREAKOUT | 195065 | 195080 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 178259 | 178296 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 177353 | 176900 | 504 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 173047 | 162042 | 15229 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 171458 | 160023 | 11963 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 171991 | 170512 | 1579 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 194148 | 193312 | 873 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 194124 | 194143 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 43028 | 43028 | 27762 | 74 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2591 | 2591 | 2252 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 69 | 69 | 69 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 54861 | 54861 | 50497 | 114 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 9 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 58192 | 58192 | 58118 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 60 | 60 | 60 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2456 | 2456 | 1730 | 8 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 62636 | 62636 | 31873 | 181 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 7742 | 7742 | 7578 | 4 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2355 | 2355 | 1154 | 6 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=193720): breakout_not_found=100923, basic_filters_failed=53276, retest_proximity_failed=32445, volume_spike_missing=5001, ema_alignment_reject=1585, missing_fvg_or_orderblock=490
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=178251): cls_disabled_merged_into_lsr=178251
- **EVAL::DIVERGENCE_CONTINUATION** (total=167297): cvd_divergence_failed=58185, basic_filters_failed=42970, h1_trend_not_aligned=35355, ema_alignment_reject=18989, cvd_insufficient=6208, retest_proximity_failed=1910, regime_blocked=1681, missing_fvg_or_orderblock=1004, missing_cvd=995
- **EVAL::FAILED_AUCTION_RECLAIM** (total=162946): auction_not_detected=65082, basic_filters_failed=41314, reclaim_hold_failed=27484, tail_too_small=23044, regime_blocked=6018, rsi_reject=4
- **EVAL::FUNDING_EXTREME** (total=199040): funding_not_extreme=126107, basic_filters_failed=48582, missing_funding_rate=21964, ema_alignment_reject=1498, rsi_reject=474, cvd_divergence_failed=221, momentum_reject=158, missing_fvg_or_orderblock=36
- **EVAL::LIQUIDATION_REVERSAL** (total=194103): cascade_threshold_not_met=137499, basic_filters_failed=53272, cvd_divergence_failed=1118, rsi_reject=1110, missing_cvd=985, missing_fvg_or_orderblock=104, volume_spike_missing=15
- **EVAL::MA_CROSS_TREND_SHIFT** (total=178761): no_ma_cross=133227, basic_filters_failed=42982, ma_cross_cooldown=1624, ma_cross_htf_unconfirmed=475, ma_cross_htf_misaligned=453
- **EVAL::MOVER_TREND_PULLBACK** (total=179097): no_ma_stack=80471, basic_filters_failed=52483, no_reclaim=21270, mover_run_too_small=20343, no_pullback_tag=3275, not_mover_context=1255
- **EVAL::OPENING_RANGE_BREAKOUT** (total=195080): feature_disabled=195080
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=178296): regime_blocked=135005, breakout_not_found=26957, basic_filters_failed=13903, adx_reject=2406, ema_alignment_reject=25
- **EVAL::QUIET_COMPRESSION_BREAK** (total=176900): compression_not_detected=86594, regime_blocked=49065, basic_filters_failed=27396, breakout_not_detected=12772, volume_confirmation_failed=928, rsi_reject=134, missing_fvg_or_orderblock=11
- **EVAL::SR_FLIP_RETEST** (total=162042): basic_filters_failed=41293, retest_out_of_zone=40050, reclaim_hold_failed=37439, flip_close_not_confirmed=30172, regime_blocked=5988, wick_quality_failed=4552, ema_alignment_reject=1630, missing_fvg_or_orderblock=909, rsi_reject=9
- **EVAL::STANDARD** (total=160023): momentum_reject=46348, adx_reject=33459, sweeps_not_detected=28998, basic_filters_failed=21102, macd_reject=17718, ema_alignment_reject=10278, invalid_sl_geometry=1812, rsi_reject=296, mtf_reject=12
- **EVAL::TREND_PULLBACK** (total=170512): h1_trend_not_aligned=46033, ema_alignment_reject=32705, basic_filters_failed=23284, h1_pullback_not_confirmed=21601, ema_not_tested_prev=15785, no_ema_reclaim_close=11778, body_conviction_fail=5923, rsi_reject=5168, regime_blocked=4171, prev_already_below_emas=1273, no_prev_low_break=1065, prev_already_above_emas=609, momentum_flat=497, no_prev_high_break=345, ema21_not_tagged=152, missing_fvg_or_orderblock=71, momentum_reject=52
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=193312): breakout_not_found=104426, basic_filters_failed=53273, retest_proximity_failed=27774, volume_spike_missing=6165, ema_alignment_reject=1278, missing_fvg_or_orderblock=351, rsi_reject=45
- **EVAL::WHALE_MOMENTUM** (total=194143): momentum_reject=148490, recent_ticks_insufficient=33360, basic_filters_failed=12293

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 446749 | 44.5% |
| QUIET | 239041 | 23.8% |
| TRENDING_DOWN | 149843 | 14.9% |
| TRENDING_UP | 109446 | 10.9% |
| VOLATILE | 59501 | 5.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **710**
- Average confidence gap to threshold: **15.10** (samples=710) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=151, SPYUSDT=72, LINKUSDT=70, SNDKUSDT=51, MSTRUSDT=38, LTCUSDT=33, 1000PEPEUSDT=31, XRPUSDT=29, SUIUSDT=26, AVAXUSDT=23

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 329 |
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 9 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 962 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 817 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 15 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 269 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 808 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 143 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 4206 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 65 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 13 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 575 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 68 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 859 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 43 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 490 |
| SR_FLIP_RETEST | filtered | min_confidence | 3160 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 421 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3852 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 74 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 731 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 6 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 56 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 5 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 338 | 62.59 | 65.00 | 2.41 | 20.69 | 19.63 | 19.51 | 0.00 | 7.06 |
| BREAKDOWN_SHORT | kept | 962 | 72.95 | 65.00 | -7.95 | 21.00 | 19.74 | 18.67 | 0.00 | 2.44 |
| DIVERGENCE_CONTINUATION | filtered | 832 | 58.64 | 65.00 | 6.36 | 20.39 | 19.62 | 17.70 | 1.19 | 10.43 |
| DIVERGENCE_CONTINUATION | kept | 269 | 69.07 | 65.00 | -4.07 | 20.64 | 19.79 | 17.73 | 2.94 | 2.76 |
| FAILED_AUCTION_RECLAIM | filtered | 951 | 57.13 | 65.00 | 7.87 | 20.79 | 19.40 | 20.00 | 4.26 | 7.10 |
| FAILED_AUCTION_RECLAIM | kept | 4206 | 67.77 | 65.00 | -2.77 | 20.47 | 19.50 | 20.00 | 4.51 | 0.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 65 | 46.10 | 65.00 | 18.90 | 21.08 | 19.53 | 17.00 | 0.55 | 7.46 |
| FUNDING_EXTREME_SIGNAL | kept | 13 | 67.92 | 65.00 | -2.92 | 20.14 | 20.00 | 16.25 | 2.92 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 643 | 54.38 | 65.00 | 10.62 | 20.46 | 19.69 | 18.46 | 2.94 | 5.04 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 859 | 70.52 | 65.00 | -5.52 | 20.95 | 19.61 | 18.12 | 2.58 | 0.45 |
| QUIET_COMPRESSION_BREAK | filtered | 43 | 58.48 | 65.00 | 6.52 | 21.60 | 20.00 | 20.00 | 0.00 | 8.20 |
| QUIET_COMPRESSION_BREAK | kept | 490 | 74.01 | 65.00 | -9.01 | 21.35 | 19.39 | 20.00 | 0.00 | 0.05 |
| SR_FLIP_RETEST | filtered | 3581 | 56.70 | 65.00 | 8.30 | 21.00 | 19.89 | 16.30 | 1.73 | 7.58 |
| SR_FLIP_RETEST | kept | 3852 | 70.57 | 65.00 | -5.57 | 21.30 | 19.93 | 15.86 | 2.17 | -0.21 |
| TREND_PULLBACK_EMA | kept | 74 | 79.87 | 65.00 | -14.87 | 20.74 | 19.72 | 18.76 | 5.15 | 0.52 |
| VOLUME_SURGE_BREAKOUT | filtered | 737 | 55.45 | 65.00 | 9.55 | 20.65 | 18.81 | 19.80 | 1.76 | 6.23 |
| VOLUME_SURGE_BREAKOUT | kept | 56 | 79.20 | 65.00 | -14.20 | 21.44 | 19.19 | 19.92 | 2.04 | 1.84 |
| WHALE_MOMENTUM | filtered | 5 | 32.70 | 65.00 | 32.30 | 23.00 | 20.00 | 17.00 | 0.00 | 21.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 338 | 62.59 | 16.60 | 16.11 | 13.13 | 12.06 | 5.56 | 6.19 | 0.00 |
| BREAKDOWN_SHORT | kept | 962 | 72.95 | 20.92 | 16.07 | 12.84 | 11.95 | 5.75 | 7.85 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 832 | 58.64 | 23.77 | 12.75 | 6.19 | 12.43 | 5.54 | 7.54 | 1.19 |
| DIVERGENCE_CONTINUATION | kept | 269 | 69.07 | 23.48 | 14.65 | 5.02 | 12.19 | 5.67 | 8.50 | 2.94 |
| FAILED_AUCTION_RECLAIM | filtered | 951 | 57.13 | 21.43 | 17.25 | 6.95 | 11.45 | 6.01 | 5.48 | 4.26 |
| FAILED_AUCTION_RECLAIM | kept | 4206 | 67.77 | 18.91 | 17.07 | 3.47 | 11.76 | 5.18 | 6.96 | 4.51 |
| FUNDING_EXTREME_SIGNAL | filtered | 65 | 46.10 | 25.00 | 8.00 | 3.83 | 17.00 | 8.10 | 6.07 | 0.55 |
| FUNDING_EXTREME_SIGNAL | kept | 13 | 67.92 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.00 | 2.92 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 643 | 54.38 | 23.30 | 14.18 | 5.73 | 12.38 | 5.19 | 5.91 | 2.94 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 859 | 70.52 | 23.12 | 14.16 | 5.90 | 12.38 | 6.05 | 6.97 | 2.58 |
| QUIET_COMPRESSION_BREAK | filtered | 43 | 58.48 | 20.35 | 18.00 | 7.74 | 15.53 | 6.72 | 3.28 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 490 | 74.01 | 17.64 | 16.65 | 11.71 | 13.99 | 7.40 | 7.56 | 0.00 |
| SR_FLIP_RETEST | filtered | 3581 | 56.70 | 19.94 | 16.82 | 5.35 | 13.40 | 5.98 | 6.83 | 1.73 |
| SR_FLIP_RETEST | kept | 3852 | 70.57 | 21.92 | 15.21 | 4.77 | 13.46 | 5.59 | 8.55 | 2.17 |
| TREND_PULLBACK_EMA | kept | 74 | 79.87 | 20.03 | 18.00 | 7.60 | 13.95 | 7.61 | 8.59 | 5.15 |
| VOLUME_SURGE_BREAKOUT | filtered | 737 | 55.45 | 17.72 | 15.95 | 13.68 | 13.72 | 5.58 | 6.00 | 1.76 |
| VOLUME_SURGE_BREAKOUT | kept | 56 | 79.20 | 21.14 | 15.25 | 14.20 | 14.86 | 7.50 | 9.00 | 2.04 |
| WHALE_MOMENTUM | filtered | 5 | 32.70 | 25.00 | 8.00 | 9.00 | 17.00 | 5.00 | 5.30 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 338 | 62.59 | 0.00 | 0.00 | 0.73 | 0.00 | 0.77 | 0.00 | 0.00 | 0.62 | **2.12** |
| BREAKDOWN_SHORT | kept | 962 | 72.95 | 0.00 | 0.00 | 0.18 | 0.00 | 0.05 | 0.01 | 0.00 | 0.07 | **0.31** |
| DIVERGENCE_CONTINUATION | filtered | 832 | 58.64 | 0.00 | 0.00 | 0.59 | 0.00 | 1.56 | 0.00 | 0.00 | 0.00 | **2.15** |
| DIVERGENCE_CONTINUATION | kept | 269 | 69.07 | 0.00 | 0.00 | 0.50 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | **0.87** |
| FAILED_AUCTION_RECLAIM | filtered | 951 | 57.13 | 0.00 | 0.00 | 0.56 | 0.00 | 4.88 | 0.08 | 0.00 | 0.00 | **5.52** |
| FAILED_AUCTION_RECLAIM | kept | 4206 | 67.77 | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.02** |
| FUNDING_EXTREME_SIGNAL | filtered | 65 | 46.10 | 0.00 | 0.00 | 6.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.77** |
| FUNDING_EXTREME_SIGNAL | kept | 13 | 67.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 643 | 54.38 | 0.00 | 0.00 | 1.25 | 0.00 | 3.58 | 0.08 | 0.00 | 0.00 | **4.91** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 859 | 70.52 | 0.00 | 0.00 | 0.01 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | **0.44** |
| QUIET_COMPRESSION_BREAK | filtered | 43 | 58.48 | 0.00 | 0.00 | 0.00 | 0.00 | 2.10 | 0.00 | 0.00 | 4.77 | **6.87** |
| QUIET_COMPRESSION_BREAK | kept | 490 | 74.01 | 0.00 | 0.00 | 0.00 | 0.00 | 2.12 | 0.00 | 0.00 | 0.00 | **2.12** |
| SR_FLIP_RETEST | filtered | 3581 | 56.70 | 0.10 | 0.00 | 0.31 | 0.00 | 2.65 | 0.02 | 0.00 | 0.56 | **3.64** |
| SR_FLIP_RETEST | kept | 3852 | 70.57 | 0.00 | 0.00 | 0.17 | 0.00 | 0.21 | 0.00 | 0.00 | 0.02 | **0.40** |
| TREND_PULLBACK_EMA | kept | 74 | 79.87 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| VOLUME_SURGE_BREAKOUT | filtered | 737 | 55.45 | 0.00 | 0.00 | 0.95 | 0.00 | 1.05 | 0.00 | 0.00 | 1.37 | **3.37** |
| VOLUME_SURGE_BREAKOUT | kept | 56 | 79.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.13** |
| WHALE_MOMENTUM | filtered | 5 | 32.70 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=113 (74.3%) | PREMATURE=22 (14.5%) | NEUTRAL=17 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 91 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 33 | 5 | 0 | 0 |
| ema_crossover | 2 | 1 | 2 | 0 |
| momentum_loss | 68 | 10 | 9 | 0 |
| trailing_invalidation | 10 | 6 | 6 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 6 | 1 | 5 | 0 |
| DIVERGENCE_CONTINUATION | 17 | 5 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 19 | 3 | 2 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 25 | 4 | 5 | 0 |
| SR_FLIP_RETEST | 40 | 9 | 4 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 4 | 0 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 33 | 5 | 0 | 12.0 | 10.8 | +0.03 | **TUNE** — marginal: avg +0.03R/kill across 38 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 2 | 1 | 2 | 1.1 | 2.0 | -0.17 | **INSUFFICIENT_SAMPLE** — only 5 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 68 | 10 | 9 | 44.5 | 16.2 | +0.33 | **KEEP** — net-helping: avg +0.33R/kill across 87 kills (saved 44.5R vs missed 16.2R) |
| trailing_invalidation | 10 | 6 | 6 | 10.1 | 8.8 | +0.06 | **TUNE** — marginal: avg +0.06R/kill across 22 kills — consider per-setup exemption or threshold adjustment, not full drop |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4799056`
- `Path funnel` emissions: `141`
- `Regime distribution` emissions: `141`
- `QUIET_SCALP_BLOCK` events: `710`
- `confidence_gate` events: `17976`
- `free_channel_post` events: `88`
- `pre_tp_fire` events: `43`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **43**
- Avg resolved threshold: **0.479%** raw → avg net **+4.09%** @ 10x
- Avg time-to-fire from dispatch: **254s**
- By threshold source: stamped=43

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 14 | 0.436% | +3.66% | 283 | stamped=14 |
| LIQUIDITY_SWEEP_REVERSAL | 14 | 0.578% | +5.08% | 157 | stamped=14 |
| FAILED_AUCTION_RECLAIM | 8 | 0.404% | +3.34% | 364 | stamped=8 |
| DIVERGENCE_CONTINUATION | 7 | 0.454% | +3.84% | 265 | stamped=7 |
- Top symbols: LITEUSDT=5, MEGAUSDT=5, HOODUSDT=4, AGTUSDT=4, FOLKSUSDT=4, APTUSDT=4, BRUSDT=3, SNDKUSDT=3, MITOUSDT=3, HUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 4954 | 4954 | 4954 | 0 |
| futures_liq | 3 | 3015 | 3015 | 4707 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **88**

| Source | Count |
|---|---:|
| signal_close | 44 |
| pre_tp | 43 |
| regime_shift | 1 |

- By severity: HIGH=88

## Dependency readiness
- cvd: presence[absent=5312, present=817335] state[empty=5312, populated=817335] buckets[few=80, many=796038, none=5312, some=21217] sources[none] quality[none]
- funding_rate: presence[absent=51328, present=771319] state[empty=51328, populated=771319] buckets[few=771319, none=51328] sources[none] quality[none]
- liquidation_clusters: presence[absent=417004, present=405643] state[empty=417004, populated=405643] buckets[few=318052, none=417004, some=87591] sources[none] quality[none]
- oi_snapshot: presence[absent=49445, present=773202] state[empty=49445, populated=773202] buckets[many=773202, none=49445] sources[none] quality[none]
- order_book: presence[absent=205720, present=616927] state[populated=616927, unavailable=205720] buckets[few=616927, none=205720] sources[book_ticker=616927, unavailable=205720] quality[none=205720, top_of_book_only=616927]
- orderblocks: presence[absent=822647] state[empty=822647] buckets[none=822647] sources[not_implemented=822647] quality[none]
- recent_ticks: presence[absent=20025, present=802622] state[empty=20025, populated=802622] buckets[many=802622, none=20025] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.607470989227295` sec
- Median create→first breach: `468.010617017746` sec
- Median create→terminal: `466.3473861217499` sec
- Median first breach→terminal: `1.2141799926757812` sec
- Fast-failure buckets: `{"under_120s": {"count": 7, "pct": 16.3}, "under_180s": {"count": 10, "pct": 23.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 5, "pct": 11.6}}`
- ~3 minute terminal-close behavior: `{"count": 6, "pct": 7.8}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 11 | 11 | 0.0 | 0.0 | 0.0 | 0.0 | 0.445 | 1469.1615935564041 | 845.1153898239136 |
| DIVERGENCE_CONTINUATION | 12 | 12 | 0.0 | 16.7 | 0.0 | 58.3 | -0.0407 | 345.7143249511719 | 345.86692440509796 |
| FAILED_AUCTION_RECLAIM | 11 | 11 | 0.0 | 0.0 | 0.0 | 72.7 | 0.1796 | 888.1656260490417 | 911.2192339897156 |
| LIQUIDITY_SWEEP_REVERSAL | 22 | 22 | 0.0 | 4.5 | 0.0 | 63.6 | -0.0235 | 240.33929300308228 | 251.16492891311646 |
| SR_FLIP_RETEST | 21 | 21 | 0.0 | 0.0 | 0.0 | 66.7 | 0.1203 | 500.76396656036377 | 474.1690684556961 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0994 | None | 539.2102445363998 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 62636 | 181 | 31873 | 0.0 | 0.0 | 500.76396656036377 | 474.1690684556961 | 30763 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 7742 | 4 | 7578 | 0.0 | 0.0 | None | None | 164 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `158`
- Gating Δ: `57360`
- No-generation Δ: `447626`
- Fast failures Δ: `-6`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 0.6669, "current_avg_pnl": 0.445, "current_win_rate": 0.0, "previous_avg_pnl": -0.2219, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0605, "current_avg_pnl": -0.0407, "current_win_rate": 0.0, "previous_avg_pnl": 0.0198, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.2093, "current_avg_pnl": 0.1796, "current_win_rate": 0.0, "previous_avg_pnl": -0.0297, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0706, "current_avg_pnl": -0.0235, "current_win_rate": 0.0, "previous_avg_pnl": -0.0941, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1148, "current_avg_pnl": 0.1203, "current_win_rate": 0.0, "previous_avg_pnl": 0.0055, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 91, "geometry_changed_delta": 0, "geometry_preserved_delta": 13799, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 232.58, "median_terminal_delta_sec": 175.57, "sl_rate_delta": -16.7, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 121, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -651.72, "median_terminal_delta_sec": -525.02, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **MOVER_TREND_PULLBACK**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
