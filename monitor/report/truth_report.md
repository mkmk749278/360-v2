# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `5981` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 21 | 21 | 21 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12391 | 12391 | 11224 | 8 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 61719 | 61727 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 59712 | 59721 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 59393 | 55968 | 3737 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 59737 | 57528 | 2330 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 60529 | 60440 | 117 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 51573 | 51584 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 59860 | 59873 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 64330 | 68147 | 879 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 61739 | 56821 | 7485 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 58207 | 58209 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 59722 | 59731 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 59357 | 59211 | 180 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 57004 | 56534 | 2783 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 50401 | 47178 | 3489 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 50673 | 50359 | 340 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 61695 | 61715 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 51587 | 51539 | 88 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7336 | 7336 | 5752 | 32 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 238 | 238 | 220 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14543 | 14543 | 14259 | 5 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 9 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1764 | 1764 | 1763 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 21556 | 21556 | 18808 | 28 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1098 | 1098 | 963 | 7 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 10506 | 10506 | 7088 | 17 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1052 | 1052 | 994 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 47 | 47 | 21 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2692 | 2692 | 2612 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=61727): breakout_not_found=30180, basic_filters_failed=20006, move_not_fresh=8469, breakout_stale=2444, retest_proximity_failed=499, volume_spike_missing=129
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=59721): cls_disabled_merged_into_lsr=59721
- **EVAL::DIVERGENCE_CONTINUATION** (total=55968): cvd_divergence_failed=19178, basic_filters_failed=16485, h1_trend_not_aligned=12239, ema_alignment_reject=7086, retest_proximity_failed=388, missing_fvg_or_orderblock=360, regime_blocked=232
- **EVAL::FAILED_AUCTION_RECLAIM** (total=57528): auction_not_detected=22326, basic_filters_failed=16303, reclaim_hold_failed=10058, tail_too_small=7661, regime_blocked=1163, rsi_reject=17
- **EVAL::FUNDING_EXTREME** (total=60440): funding_not_extreme=41747, basic_filters_failed=16319, missing_funding_rate=1149, ema_alignment_reject=901, rsi_reject=174, cvd_divergence_failed=90, momentum_reject=53, missing_fvg_or_orderblock=7
- **EVAL::LIQUIDATION_REVERSAL** (total=51584): cascade_threshold_not_met=34862, basic_filters_failed=16455, cvd_divergence_failed=149, rsi_reject=104, missing_fvg_or_orderblock=11, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=59873): no_ma_cross=41862, basic_filters_failed=16496, ma_cross_cooldown=1089, ma_cross_htf_misaligned=426
- **EVAL::MOVER_AVWAP_SCALP** (total=68147): no_avwap_tag=30180, basic_filters_failed=20130, no_mover_leg=12166, avwap_slope_against=3884, no_avwap_reclaim=927, avwap_reclaim_no_volume=860
- **EVAL::MOVER_TREND_PULLBACK** (total=56821): mover_run_too_small=23805, basic_filters_failed=20074, no_reclaim=11192, no_pullback_tag=1750
- **EVAL::OPENING_RANGE_BREAKOUT** (total=58209): feature_disabled=58209
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=59731): regime_blocked=41098, breakout_not_found=11683, basic_filters_failed=4892, adx_reject=2039, ema_alignment_reject=17, rsi_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=59211): compression_not_detected=22197, regime_blocked=19724, basic_filters_failed=11402, breakout_not_detected=5359, volume_confirmation_failed=477, rsi_reject=45, missing_fvg_or_orderblock=7
- **EVAL::SR_FLIP_RETEST** (total=56534): basic_filters_failed=16285, flip_close_not_confirmed=9202, whipsaw_flip=7949, long_break_volume_thin=7139, reclaim_hold_failed=4688, long_disabled=4668, retest_out_of_zone=3453, wick_quality_failed=1496, regime_blocked=1160, long_acceptance_not_held=254, missing_fvg_or_orderblock=190, ema_alignment_reject=50
- **EVAL::STANDARD** (total=47178): momentum_reject=13741, adx_reject=11744, basic_filters_failed=7823, sweeps_not_detected=6679, macd_reject=4513, ema_alignment_reject=2477, invalid_sl_geometry=119, rsi_reject=82
- **EVAL::TREND_PULLBACK** (total=50359): h1_trend_not_aligned=14292, h1_pullback_not_confirmed=10841, ema_alignment_reject=8016, basic_filters_failed=7759, no_ema_reclaim_close=2783, ema_not_tested_prev=1815, body_conviction_fail=1804, rsi_reject=1455, regime_blocked=375, prev_already_above_emas=330, prev_already_below_emas=314, no_prev_high_break=243, no_prev_low_break=180, momentum_flat=69, missing_fvg_or_orderblock=37, momentum_reject=30, ema21_not_tagged=16
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=61715): breakout_not_found=33891, basic_filters_failed=20003, move_not_fresh=4852, breakout_stale=2236, retest_proximity_failed=540, volume_spike_missing=183, ema_alignment_reject=9, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=51539): momentum_reject=38042, recent_ticks_insufficient=9862, basic_filters_failed=3635

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 101119 | 34.6% |
| RANGING | 84947 | 29.1% |
| TRENDING_DOWN | 57057 | 19.5% |
| TRENDING_UP | 39886 | 13.7% |
| VOLATILE | 9034 | 3.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **178**
- Average confidence gap to threshold: **17.10** (samples=178) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: IBMUSDT=43, AMDUSDT=17, FILUSDT=16, 1000PEPEUSDT=14, BTCUSDT=13, ENAUSDT=12, XLMUSDT=12, TAOUSDT=7, AAVEUSDT=5, ORCLUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 176 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 9 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 162 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 295 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 65 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 296 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 17 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 313 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2086 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 34 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 18 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 7 |
| SR_FLIP_RETEST | filtered | min_confidence | 215 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 79 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 246 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 16 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 42 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 185 | 48.93 | 65.00 | 16.07 | 19.74 | 19.94 | 17.63 | 0.61 | 14.27 |
| DIVERGENCE_CONTINUATION | kept | 162 | 70.18 | 65.00 | -5.18 | 19.40 | 19.96 | 16.99 | 2.32 | -2.55 |
| FAILED_AUCTION_RECLAIM | filtered | 360 | 53.92 | 65.00 | 11.08 | 20.07 | 19.24 | 20.00 | 4.61 | 5.79 |
| FAILED_AUCTION_RECLAIM | kept | 296 | 71.55 | 65.00 | -6.55 | 20.54 | 19.32 | 20.00 | 4.13 | 1.27 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 52.93 | 65.00 | 12.07 | 21.71 | 20.00 | 16.84 | 2.00 | 18.23 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 69.23 | 65.00 | -4.23 | 20.80 | 19.92 | 17.18 | 2.41 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 79.50 | 65.00 | -14.50 | 18.80 | 18.10 | 15.80 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 313 | 58.05 | 65.00 | 6.95 | 19.44 | 16.83 | 15.80 | 4.81 | 5.24 |
| MOVER_TREND_PULLBACK | kept | 2086 | 75.41 | 65.00 | -10.41 | 20.40 | 18.46 | 15.80 | 4.71 | 0.32 |
| QUIET_COMPRESSION_BREAK | filtered | 52 | 54.24 | 65.00 | 10.76 | 20.12 | 19.48 | 20.00 | 0.00 | 13.33 |
| QUIET_COMPRESSION_BREAK | kept | 7 | 70.41 | 65.00 | -5.41 | 21.51 | 19.10 | 20.00 | 0.00 | 0.47 |
| SR_FLIP_RETEST | filtered | 294 | 54.03 | 65.00 | 10.97 | 20.56 | 19.89 | 15.94 | 2.28 | 18.22 |
| SR_FLIP_RETEST | kept | 246 | 70.71 | 65.00 | -5.71 | 21.29 | 19.88 | 15.84 | 2.34 | -1.73 |
| TREND_PULLBACK_EMA | filtered | 16 | 51.90 | 65.00 | 13.10 | 18.56 | 19.80 | 20.00 | 5.50 | 21.80 |
| TREND_PULLBACK_EMA | kept | 42 | 83.35 | 65.00 | -18.35 | 19.88 | 19.69 | 17.41 | 5.46 | -2.81 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 79.40 | 65.00 | -14.40 | 18.80 | 18.95 | 20.00 | 5.50 | 9.10 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 185 | 48.93 | 23.40 | 16.22 | 3.66 | 12.58 | 6.81 | 7.22 | 0.61 |
| DIVERGENCE_CONTINUATION | kept | 162 | 70.18 | 22.38 | 13.49 | 4.20 | 13.28 | 6.11 | 8.57 | 2.32 |
| FAILED_AUCTION_RECLAIM | filtered | 360 | 53.92 | 23.33 | 15.89 | 4.44 | 11.46 | 6.66 | 5.10 | 4.61 |
| FAILED_AUCTION_RECLAIM | kept | 296 | 71.55 | 23.55 | 15.41 | 5.47 | 11.71 | 6.23 | 6.32 | 4.13 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 52.93 | 24.06 | 14.00 | 6.53 | 11.65 | 5.82 | 7.14 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 69.23 | 25.00 | 14.00 | 4.59 | 12.47 | 7.85 | 2.91 | 2.41 |
| MOVER_AVWAP_SCALP | kept | 1 | 79.50 | 17.00 | 18.00 | 7.50 | 14.00 | 10.00 | 10.00 | 3.00 |
| MOVER_TREND_PULLBACK | filtered | 313 | 58.05 | 17.52 | 18.00 | 8.01 | 12.73 | 6.01 | 7.27 | 4.81 |
| MOVER_TREND_PULLBACK | kept | 2086 | 75.41 | 19.89 | 18.00 | 7.78 | 12.47 | 5.61 | 8.25 | 4.71 |
| QUIET_COMPRESSION_BREAK | filtered | 52 | 54.24 | 17.62 | 15.38 | 13.21 | 14.00 | 6.27 | 2.53 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 7 | 70.41 | 18.14 | 16.29 | 10.71 | 14.00 | 5.50 | 6.67 | 0.00 |
| SR_FLIP_RETEST | filtered | 294 | 54.03 | 22.07 | 15.31 | 7.15 | 13.42 | 5.86 | 6.16 | 2.28 |
| SR_FLIP_RETEST | kept | 246 | 70.71 | 23.05 | 17.11 | 4.22 | 13.06 | 5.60 | 5.98 | 2.34 |
| TREND_PULLBACK_EMA | filtered | 16 | 51.90 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 6.70 | 5.50 |
| TREND_PULLBACK_EMA | kept | 42 | 83.35 | 24.81 | 18.00 | 7.50 | 14.00 | 5.00 | 8.69 | 5.46 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 79.40 | 25.00 | 14.00 | 15.00 | 14.00 | 5.00 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 185 | 48.93 | 0.00 | 0.00 | 1.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.22** |
| DIVERGENCE_CONTINUATION | kept | 162 | 70.18 | 0.00 | 0.00 | 0.12 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.16** |
| FAILED_AUCTION_RECLAIM | filtered | 360 | 53.92 | 0.00 | 0.00 | 2.12 | 0.00 | 2.70 | 0.00 | 0.00 | 0.00 | **4.82** |
| FAILED_AUCTION_RECLAIM | kept | 296 | 71.55 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.10** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 52.93 | 0.00 | 0.00 | 10.64 | 0.00 | 5.08 | 0.00 | 0.00 | 0.00 | **15.72** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 69.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 1 | 79.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 313 | 58.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 2086 | 75.41 | 0.00 | 0.00 | 0.07 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.10** |
| QUIET_COMPRESSION_BREAK | filtered | 52 | 54.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.99 | 0.00 | 0.00 | 7.66 | **8.65** |
| QUIET_COMPRESSION_BREAK | kept | 7 | 70.41 | 0.00 | 0.00 | 0.00 | 0.00 | 2.19 | 0.00 | 0.00 | 0.00 | **2.19** |
| SR_FLIP_RETEST | filtered | 294 | 54.03 | 0.00 | 0.00 | 2.74 | 0.00 | 5.35 | 0.00 | 0.00 | 2.60 | **10.69** |
| SR_FLIP_RETEST | kept | 246 | 70.71 | 0.00 | 0.00 | 0.05 | 0.00 | 0.08 | 0.00 | 0.00 | 0.21 | **0.34** |
| TREND_PULLBACK_EMA | filtered | 16 | 51.90 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| TREND_PULLBACK_EMA | kept | 42 | 83.35 | 0.00 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.11** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 79.40 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | 0.00 | 0.00 | 0.00 | **3.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=1 (50.0%) | PREMATURE=0 (0.0%) | NEUTRAL=1 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 1 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 1 | 0 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1 | 0 |
| MOVER_AVWAP_SCALP | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 1 | 0 | 1 | 0.9 | 0.0 | +0.44 | **INSUFFICIENT_SAMPLE** — only 2 classified kills (need >= 20); let data accumulate before tuning |

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=564 (12.7%) | WOULD_LOSE=1510 | WOULD_EXPIRE=2368 | pending (awaiting window)=544

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| data_stale | 2 | 100.0% | 0.0 | 0.4 | -0.21 | **INSUFFICIENT_SAMPLE** |
| dispatch_staleness | 1401 | 10.1% | 208.0 | 59.2 | +0.11 | **KEEP** |
| level_still_in_play | 836 | 13.6% | 86.0 | 46.6 | +0.05 | **TUNE** |
| min_confidence | 1554 | 7.7% | 1010.0 | 196.4 | +0.52 | **KEEP** |
| quiet_scalp_block | 269 | 5.2% | 82.0 | 16.8 | +0.24 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 9 | 11.1% | 4.0 | 0.7 | +0.36 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 47 | 59.6% | 19.0 | 21.0 | -0.04 | **TUNE** |
| shadow_unit:SHADOW_MEAN_REVERT | 191 | 58.1% | 74.0 | 234.3 | -0.84 | **DROP** |
| shadow_unit:SHADOW_RANGE_FADE | 133 | 24.8% | 27.0 | 130.2 | -0.78 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 11195 across 15 strategies; 237 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 3293 | 7/3286/0 | 35% | -0.29 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (+1.15R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 2377 | 0/2377/0 | 43% | -0.11 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.54R) | LONDON/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 1806 | 3/1803/0 | 41% | +0.03 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.78R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 1119 | 1/1118/0 | 37% | -0.18 | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL (+0.94R) | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_MEAN_REVERT | 550 | 0/0/550 | 59% | +0.67 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.62R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.45R) |
| SHADOW_RANGE_FADE | 396 | 0/0/396 | 50% | +0.67 | NY/RANGE/NORMAL/BTC_NEUTRAL (+1.97R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+0.15R) |
| SHADOW_FUNDING_FADE | 384 | 0/0/384 | 39% | -0.32 | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-0.46R) | NY/QUIET/COMPRESSED/BTC_FALLING (-0.90R) |
| QUIET_COMPRESSION_BREAK | 359 | 0/359/0 | 55% | -0.12 | NY/QUIET/NORMAL/BTC_NEUTRAL (+0.52R) | NY/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 359 | 0/359/0 | 23% | -0.39 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (-0.06R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 162 | 0/162/0 | 24% | -0.15 | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (+0.15R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.51R) |
| MOVER_AVWAP_SCALP | 141 | 4/137/0 | 12% | -0.78 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 85 | 1/84/0 | 1% | -0.78 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 70 | 0/70/0 | 67% | +0.61 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 70 | 0/70/0 | 20% | -0.14 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.44R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.44R) |
| SHADOW_CASCADE_REVERSAL | 24 | 0/0/24 | 58% | +0.06 | — | — |

- **Strongest cells**: `SHADOW_RANGE_FADE @ NY/RANGE/NORMAL/BTC_NEUTRAL` +1.97R (n=19, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.78R (n=42, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL` +1.77R (n=29, STRONG)
- **Weakest cells**: `SR_FLIP_RETEST @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL` -1.00R (n=31, NEGATIVE); `DIVERGENCE_CONTINUATION @ NY/MARKDOWN/NORMAL/BTC_NEUTRAL` -1.00R (n=39, NEGATIVE); `FAILED_AUCTION_RECLAIM @ NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.00R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 84 | 39% / -0.16R | 84 | 39% / -0.05R | +0.11 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 16 | 31% / -0.24R | 16 | 31% / -0.34R | -0.10 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 65 | 35% / -0.12R | 65 | 35% / -0.08R | +0.04 | **ATR** |
| QUIET_COMPRESSION_BREAK | 17 | 41% / -0.09R | 17 | 41% / -0.06R | +0.04 | **ATR** |
| MOVER_TREND_PULLBACK | 54 | 52% / -0.07R | 54 | 56% / -0.04R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 10 | 50% / -0.08R | 10 | 50% / -0.20R | — | **MEASURING** |
| WHALE_MOMENTUM | 8 | 25% / -0.04R | 8 | 25% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 6 | 83% / +0.34R | 6 | 83% / +0.23R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 1 | 0% / -1.00R | 1 | 0% / -0.13R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 7 · alerting: **0** · boot grace active: False

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| btc_reference | ok | BTC ref 64644.70 | 0 |
| candle_coverage | ok | 87/88 symbols with ≥20 15m candles | 0 |
| geometry_ab | ok | output +2 / upstream +69 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| strategy_edge | ok | output +38 / upstream +69 | 0 |
| suppression_audit | ok | output +69 / upstream +32 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `79675`
- `Path funnel` emissions: `35`
- `Regime distribution` emissions: `35`
- `QUIET_SCALP_BLOCK` events: `178`
- `confidence_gate` events: `4096`
- `free_channel_post` events: `3`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 6 | 5823 | 7692 | 8532 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| signal_close | 3 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[present=248471] state[populated=248471] buckets[many=248467, some=4] sources[none] quality[none]
- funding_rate: presence[absent=24770, present=223701] state[empty=24770, populated=223701] buckets[few=223701, none=24770] sources[none] quality[none]
- liquidation_clusters: presence[absent=160249, present=88222] state[empty=160249, populated=88222] buckets[few=75561, none=160249, some=12661] sources[none] quality[none]
- oi_snapshot: presence[absent=23618, present=224853] state[empty=23618, populated=224853] buckets[many=224853, none=23618] sources[none] quality[none]
- order_book: presence[absent=67589, present=180882] state[populated=180882, unavailable=67589] buckets[few=180882, none=67589] sources[book_ticker=180882, unavailable=67589] quality[none=67589, top_of_book_only=180882]
- orderblocks: presence[absent=248471] state[empty=248471] buckets[none=248471] sources[not_implemented=248471] quality[none]
- recent_ticks: presence[absent=2689, present=245782] state[empty=2689, populated=245782] buckets[many=245782, none=2689] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.7942910194396973` sec
- Median create→first breach: `2199.094582557678` sec
- Median create→terminal: `2398.705082178116` sec
- Median first breach→terminal: `3.090809464454651` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.904 | 345.69719195365906 | 347.7854850292206 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 50.0 | 50.0 | 50.0 | 0.0 | 1.0293 | 4777.261600494385 | 4780.352409958839 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.15 | 5552.605817079544 | 5554.107434988022 |
| MOVER_TREND_PULLBACK | 4 | 4 | 0.0 | 25.0 | 0.0 | 0.0 | 1.7067 | 984.4026601314545 | 1431.794086098671 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 10506 | 17 | 7088 | 0.0 | 0.0 | None | None | 3418 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1052 | 1 | 994 | 0.0 | 0.0 | None | None | 58 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `100`
- Gating Δ: `63735`
- No-generation Δ: `976285`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 3.4572, "current_avg_pnl": 1.0293, "current_win_rate": 50.0, "previous_avg_pnl": -2.4279, "previous_win_rate": 0.0, "win_rate_delta": 50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.7807, "current_avg_pnl": 1.7067, "current_win_rate": 0.0, "previous_avg_pnl": 0.926, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 17, "geometry_changed_delta": 0, "geometry_preserved_delta": 3418, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 58, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
