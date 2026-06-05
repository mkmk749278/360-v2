# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `1148` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2635 | 2635 | 263 | 8 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 22322 | 22322 | 18054 | 42 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 78511 | 78048 | 500 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 72394 | 72402 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 71985 | 66882 | 5504 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 72409 | 70052 | 2503 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 78995 | 78920 | 90 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 78468 | 78475 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 72558 | 72569 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 78549 | 78552 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 72401 | 72405 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 71971 | 71944 | 38 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 71512 | 66822 | 5129 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 71013 | 64257 | 7117 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 71380 | 70648 | 789 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 78486 | 78382 | 128 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 78479 | 78483 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 9300 | 9300 | 7055 | 46 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 508 | 508 | 480 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 28622 | 28622 | 24858 | 141 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 13 | 0 | low-sample (none) |
| MOMENTUM_EXPANSION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 143 | 143 | 109 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 19548 | 19548 | 7261 | 249 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3838 | 3838 | 3821 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 868 | 868 | 513 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=78048): breakout_not_found=43125, basic_filters_failed=16467, retest_proximity_failed=14064, volume_spike_missing=3283, ema_alignment_reject=788, insufficient_candles=228, missing_fvg_or_orderblock=93
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=72402): cls_disabled_merged_into_lsr=72402
- **EVAL::DIVERGENCE_CONTINUATION** (total=66882): cvd_divergence_failed=29575, basic_filters_failed=15531, h1_trend_not_aligned=10179, ema_alignment_reject=9249, retest_proximity_failed=1774, missing_fvg_or_orderblock=428, regime_blocked=146
- **EVAL::FAILED_AUCTION_RECLAIM** (total=70052): auction_not_detected=27402, basic_filters_failed=14518, reclaim_hold_failed=12378, tail_too_small=10947, regime_blocked=4807
- **EVAL::FUNDING_EXTREME** (total=78920): funding_not_extreme=60196, basic_filters_failed=16373, missing_funding_rate=1043, ema_alignment_reject=706, rsi_reject=385, momentum_reject=103, cvd_divergence_failed=89, insufficient_candles=23, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=78475): cascade_threshold_not_met=60464, basic_filters_failed=16490, cvd_divergence_failed=755, rsi_reject=566, insufficient_candles=158, volume_spike_missing=31, missing_fvg_or_orderblock=11
- **EVAL::MA_CROSS_TREND_SHIFT** (total=72569): no_ma_cross=55813, basic_filters_failed=15537, ma_cross_cooldown=1219
- **EVAL::OPENING_RANGE_BREAKOUT** (total=78552): feature_disabled=78552
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=72405): regime_blocked=59621, breakout_not_found=10441, basic_filters_failed=2285, adx_reject=29, ema_alignment_reject=24, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=71944): compression_not_detected=41158, regime_blocked=17530, basic_filters_failed=12228, breakout_not_detected=896, volume_confirmation_failed=92, rsi_reject=40
- **EVAL::SR_FLIP_RETEST** (total=66822): retest_out_of_zone=19077, reclaim_hold_failed=14518, basic_filters_failed=14513, flip_close_not_confirmed=10354, regime_blocked=4783, wick_quality_failed=2226, ema_alignment_reject=883, missing_fvg_or_orderblock=396, rsi_reject=72
- **EVAL::STANDARD** (total=64257): adx_reject=15595, momentum_reject=13849, basic_filters_failed=12213, macd_reject=10021, ema_alignment_reject=5454, sweeps_not_detected=5341, invalid_sl_geometry=1598, rsi_reject=184, mtf_reject=2
- **EVAL::TREND_PULLBACK** (total=70648): h1_pullback_not_confirmed=15753, ema_alignment_reject=13197, h1_trend_not_aligned=11237, ema_not_tested_prev=9387, basic_filters_failed=8893, no_ema_reclaim_close=4955, body_conviction_fail=2748, rsi_reject=2193, prev_already_below_emas=918, no_prev_low_break=519, momentum_flat=258, regime_blocked=226, prev_already_above_emas=202, ema21_not_tagged=83, no_prev_high_break=69, missing_fvg_or_orderblock=7, momentum_reject=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=78382): breakout_not_found=51847, basic_filters_failed=16467, retest_proximity_failed=6584, volume_spike_missing=2390, ema_alignment_reject=654, insufficient_candles=228, missing_fvg_or_orderblock=204, rsi_reject=8
- **EVAL::WHALE_MOMENTUM** (total=78483): momentum_reject=63932, recent_ticks_insufficient=11289, basic_filters_failed=3262

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 249459 | 66.0% |
| QUIET | 39096 | 10.3% |
| VOLATILE | 35459 | 9.4% |
| TRENDING_DOWN | 31097 | 8.2% |
| TRENDING_UP | 22643 | 6.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **411**
- Average confidence gap to threshold: **16.05** (samples=411) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: QQQUSDT=88, BZUSDT=86, TRXUSDT=47, CLUSDT=42, INTCUSDT=31, EWYUSDT=29, CRCLUSDT=17, AVGOUSDT=17, BNBUSDT=14, MUUSDT=9

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 185 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 45 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 716 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 23 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 418 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 571 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 79 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 779 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 933 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 55 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 727 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 4 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 3156 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 250 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2814 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 91 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 94 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 185 | 60.46 | 65.00 | 4.54 | 21.99 | 18.91 | 19.85 | 0.00 | 7.51 |
| BREAKDOWN_SHORT | kept | 45 | 68.78 | 65.00 | -3.78 | 23.10 | 19.76 | 19.11 | 0.00 | 1.11 |
| DIVERGENCE_CONTINUATION | filtered | 739 | 57.30 | 65.00 | 7.70 | 20.28 | 19.68 | 18.52 | 2.93 | 10.99 |
| DIVERGENCE_CONTINUATION | kept | 418 | 68.36 | 65.00 | -3.36 | 20.21 | 19.80 | 17.69 | 2.53 | 0.25 |
| FAILED_AUCTION_RECLAIM | filtered | 650 | 55.38 | 65.00 | 9.62 | 20.70 | 19.33 | 20.00 | 4.45 | 4.58 |
| FAILED_AUCTION_RECLAIM | kept | 779 | 71.19 | 65.00 | -6.19 | 21.07 | 19.68 | 20.00 | 4.08 | 0.61 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 44.30 | 65.00 | 20.70 | 19.80 | 19.50 | 17.00 | 0.00 | 12.00 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 76.30 | 65.00 | -11.30 | 23.10 | 19.83 | 17.00 | 1.33 | 1.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 988 | 54.54 | 65.00 | 10.46 | 21.21 | 19.36 | 18.36 | 2.70 | 6.37 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 727 | 69.74 | 65.00 | -4.74 | 21.13 | 19.42 | 17.79 | 2.44 | 0.77 |
| QUIET_COMPRESSION_BREAK | filtered | 4 | 45.30 | 65.00 | 19.70 | 19.80 | 20.00 | 20.00 | 0.00 | 22.50 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 77.00 | 65.00 | -12.00 | 21.00 | 20.00 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 3406 | 51.37 | 65.00 | 13.63 | 20.92 | 19.87 | 15.89 | 2.00 | 8.35 |
| SR_FLIP_RETEST | kept | 2814 | 72.41 | 65.00 | -7.41 | 20.65 | 19.88 | 15.81 | 1.99 | -0.63 |
| TREND_PULLBACK_EMA | kept | 91 | 79.96 | 65.00 | -14.96 | 19.68 | 19.98 | 18.39 | 5.84 | -0.18 |
| VOLUME_SURGE_BREAKOUT | filtered | 94 | 58.19 | 65.00 | 6.81 | 20.42 | 19.31 | 20.00 | 1.92 | 9.06 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 185 | 60.46 | 22.66 | 10.67 | 7.18 | 13.55 | 5.01 | 8.89 | 0.00 |
| BREAKDOWN_SHORT | kept | 45 | 68.78 | 23.93 | 10.67 | 5.47 | 13.96 | 7.83 | 8.03 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 739 | 57.30 | 22.89 | 10.35 | 6.21 | 12.48 | 5.94 | 7.79 | 2.93 |
| DIVERGENCE_CONTINUATION | kept | 418 | 68.36 | 21.84 | 14.22 | 5.12 | 11.65 | 5.64 | 8.73 | 2.53 |
| FAILED_AUCTION_RECLAIM | filtered | 650 | 55.38 | 21.73 | 17.03 | 4.74 | 11.29 | 6.75 | 4.71 | 4.45 |
| FAILED_AUCTION_RECLAIM | kept | 779 | 71.19 | 20.25 | 17.30 | 3.84 | 11.35 | 7.01 | 7.97 | 4.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 44.30 | 25.00 | 8.00 | 12.00 | 17.00 | 5.00 | 4.30 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 76.30 | 25.00 | 18.00 | 4.00 | 15.00 | 7.50 | 7.13 | 1.33 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 988 | 54.54 | 22.56 | 14.06 | 7.28 | 12.47 | 5.58 | 5.10 | 2.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 727 | 69.74 | 23.44 | 14.12 | 4.77 | 12.74 | 5.39 | 7.68 | 2.44 |
| QUIET_COMPRESSION_BREAK | filtered | 4 | 45.30 | 17.00 | 18.00 | 9.00 | 14.00 | 8.50 | 1.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 77.00 | 25.00 | 18.00 | 9.00 | 14.00 | 5.00 | 6.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 3406 | 51.37 | 21.37 | 17.27 | 4.56 | 13.54 | 6.19 | 5.30 | 2.00 |
| SR_FLIP_RETEST | kept | 2814 | 72.41 | 21.16 | 17.14 | 4.59 | 13.68 | 5.95 | 9.02 | 1.99 |
| TREND_PULLBACK_EMA | kept | 91 | 79.96 | 19.30 | 18.00 | 6.66 | 14.03 | 6.70 | 9.55 | 5.84 |
| VOLUME_SURGE_BREAKOUT | filtered | 94 | 58.19 | 18.96 | 16.94 | 4.21 | 14.56 | 4.87 | 7.78 | 1.92 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 185 | 60.46 | 0.00 | 0.00 | 0.75 | 0.00 | 2.15 | 0.00 | 0.00 | 0.34 | **3.24** |
| BREAKDOWN_SHORT | kept | 45 | 68.78 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.37** |
| DIVERGENCE_CONTINUATION | filtered | 739 | 57.30 | 0.00 | 0.00 | 1.95 | 0.00 | 3.35 | 0.00 | 0.00 | 0.00 | **5.30** |
| DIVERGENCE_CONTINUATION | kept | 418 | 68.36 | 0.47 | 0.00 | 0.22 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | **0.86** |
| FAILED_AUCTION_RECLAIM | filtered | 650 | 55.38 | 0.56 | 0.00 | 0.47 | 0.00 | 1.33 | 0.02 | 0.00 | 0.00 | **2.38** |
| FAILED_AUCTION_RECLAIM | kept | 779 | 71.19 | 0.30 | 0.00 | 0.07 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.39** |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 44.30 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 76.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 988 | 54.54 | 0.00 | 0.00 | 0.77 | 0.00 | 4.51 | 0.16 | 0.00 | 0.00 | **5.44** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 727 | 69.74 | 0.00 | 0.00 | 0.06 | 0.00 | 0.42 | 0.01 | 0.00 | 0.00 | **0.49** |
| QUIET_COMPRESSION_BREAK | filtered | 4 | 45.30 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 10.80 | **15.10** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 77.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 3406 | 51.37 | 0.09 | 0.00 | 0.77 | 0.00 | 1.19 | 0.05 | 0.00 | 1.55 | **3.65** |
| SR_FLIP_RETEST | kept | 2814 | 72.41 | 0.21 | 0.00 | 0.04 | 0.00 | 0.46 | 0.05 | 0.00 | 0.00 | **0.76** |
| TREND_PULLBACK_EMA | kept | 91 | 79.96 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| VOLUME_SURGE_BREAKOUT | filtered | 94 | 58.19 | 0.00 | 0.00 | 5.08 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | **5.46** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=131 (80.4%) | PREMATURE=24 (14.7%) | NEUTRAL=8 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 107 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 39 | 8 | 0 | 0 |
| ema_crossover | 0 | 0 | 1 | 0 |
| momentum_loss | 59 | 10 | 2 | 0 |
| regime_shift | 8 | 0 | 1 | 0 |
| trailing_invalidation | 25 | 6 | 4 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 8 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 16 | 2 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 13 | 0 | 1 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 38 | 6 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 47 | 14 | 3 | 0 |
| TREND_PULLBACK_EMA | 4 | 2 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 39 | 8 | 0 | 14.5 | 16.3 | -0.04 | **TUNE** — marginal: avg -0.04R/kill across 47 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 0 | 0 | 1 | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** — only 1 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 59 | 10 | 2 | 39.2 | 16.3 | +0.32 | **KEEP** — net-helping: avg +0.32R/kill across 71 kills (saved 39.2R vs missed 16.3R) |
| regime_shift | 8 | 0 | 1 | 4.9 | 0.0 | +0.55 | **INSUFFICIENT_SAMPLE** — only 9 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 25 | 6 | 4 | 21.2 | 8.3 | +0.37 | **KEEP** — net-helping: avg +0.37R/kill across 35 kills (saved 21.2R vs missed 8.3R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2041787`
- `Path funnel` emissions: `53`
- `Regime distribution` emissions: `53`
- `QUIET_SCALP_BLOCK` events: `411`
- `confidence_gate` events: `10946`
- `free_channel_post` events: `111`
- `pre_tp_fire` events: `49`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **49**
- Avg resolved threshold: **0.487%** raw → avg net **+4.17%** @ 10x
- Avg time-to-fire from dispatch: **258s**
- By threshold source: stamped=49

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 22 | 0.455% | +3.85% | 296 | stamped=22 |
| LIQUIDITY_SWEEP_REVERSAL | 11 | 0.514% | +4.44% | 194 | stamped=11 |
| FAILED_AUCTION_RECLAIM | 8 | 0.534% | +4.64% | 342 | stamped=8 |
| DIVERGENCE_CONTINUATION | 7 | 0.428% | +3.58% | 113 | stamped=7 |
| FUNDING_EXTREME_SIGNAL | 1 | 0.914% | +8.44% | 480 | stamped=1 |
- Top symbols: 1000PEPEUSDT=6, FILUSDT=5, XPLUSDT=5, MAGMAUSDT=4, OPUSDT=4, MYXUSDT=3, HOMEUSDT=3, WIFUSDT=3, EPICUSDT=2, APTUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **111**

| Source | Count |
|---|---:|
| signal_close | 55 |
| pre_tp | 49 |
| regime_shift | 6 |
| signal_highlight | 1 |

- By severity: HIGH=111

## Dependency readiness
- cvd: presence[present=311978] state[populated=311978] buckets[few=8, many=311909, some=61] sources[none] quality[none]
- funding_rate: presence[absent=3484, present=308494] state[empty=3484, populated=308494] buckets[few=308494, none=3484] sources[none] quality[none]
- liquidation_clusters: presence[absent=137814, present=174164] state[empty=137814, populated=174164] buckets[few=130100, none=137814, some=44064] sources[none] quality[none]
- oi_snapshot: presence[absent=706, present=311272] state[empty=706, populated=311272] buckets[few=159, many=310190, none=706, some=923] sources[none] quality[none]
- order_book: presence[absent=84716, present=227262] state[populated=227262, unavailable=84716] buckets[few=227262, none=84716] sources[book_ticker=227262, unavailable=84716] quality[none=84716, top_of_book_only=227262]
- orderblocks: presence[absent=311978] state[empty=311978] buckets[none=311978] sources[not_implemented=311978] quality[none]
- recent_ticks: presence[absent=1391, present=310587] state[empty=1391, populated=310587] buckets[many=310587, none=1391] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `15.558313131332397` sec
- Median create→first breach: `356.66953706741333` sec
- Median create→terminal: `287.676521897316` sec
- Median first breach→terminal: `3.4777750968933105` sec
- Fast-failure buckets: `{"under_120s": {"count": 14, "pct": 25.5}, "under_180s": {"count": 17, "pct": 30.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 3, "pct": 5.5}}`
- ~3 minute terminal-close behavior: `{"count": 11, "pct": 10.6}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.3198 | 462.8114809989929 | 151.6150939464569 |
| DIVERGENCE_CONTINUATION | 18 | 18 | 0.0 | 5.6 | 0.0 | 38.9 | -0.0361 | 116.38567209243774 | 135.58810114860535 |
| FAILED_AUCTION_RECLAIM | 11 | 11 | 0.0 | 9.1 | 0.0 | 72.7 | 0.1968 | 389.59827494621277 | 493.7578444480896 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 100.0 | 0.4571 | 1922.881098985672 | 1924.7788360118866 |
| LIQUIDITY_SWEEP_REVERSAL | 21 | 21 | 0.0 | 0.0 | 0.0 | 52.4 | -0.171 | 286.0523099899292 | 264.06514739990234 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.2999 | None | 976.5360758304596 |
| SR_FLIP_RETEST | 51 | 51 | 0.0 | 15.7 | 0.0 | 43.1 | -0.0851 | 400.5740519762039 | 357.65639996528625 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.1066 | None | 873.3806810379028 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 19548 | 249 | 7261 | 0.0 | 15.7 | 400.5740519762039 | 357.65639996528625 | 12287 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3838 | 2 | 3821 | 0.0 | 0.0 | None | 873.3806810379028 | 17 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-70`
- Gating Δ: `42387`
- No-generation Δ: `618706`
- Fast failures Δ: `-10`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 0.1748, "current_avg_pnl": -0.3198, "current_win_rate": 0.0, "previous_avg_pnl": -0.4946, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.1269, "current_avg_pnl": -0.0361, "current_win_rate": 0.0, "previous_avg_pnl": 0.0908, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.3272, "current_avg_pnl": 0.1968, "current_win_rate": 0.0, "previous_avg_pnl": -0.1304, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.2642, "current_avg_pnl": -0.171, "current_win_rate": 0.0, "previous_avg_pnl": 0.0932, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.087, "current_avg_pnl": -0.0851, "current_win_rate": 0.0, "previous_avg_pnl": -0.1721, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.0135, "current_avg_pnl": -0.1066, "current_win_rate": 0.0, "previous_avg_pnl": -0.0931, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -20, "geometry_changed_delta": 0, "geometry_preserved_delta": 8185, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 140.78, "median_terminal_delta_sec": 90.93, "sl_rate_delta": -0.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -11, "geometry_changed_delta": 0, "geometry_preserved_delta": -38, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -445.99, "median_terminal_delta_sec": 19.07, "sl_rate_delta": -12.5, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **VOLUME_SURGE_BREAKOUT**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
