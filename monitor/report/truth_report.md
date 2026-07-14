# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `13353` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 8897 | 8897 | 7652 | 9 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 41571 | 41574 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 35241 | 35244 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 35100 | 33038 | 2198 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 35253 | 33625 | 1722 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 37769 | 37687 | 99 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 32341 | 32344 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 35352 | 35366 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 43221 | 44689 | 924 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 41576 | 37101 | 6100 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 35954 | 35958 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 35244 | 35251 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 35090 | 35017 | 82 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 33260 | 34044 | 1022 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 29767 | 27657 | 2224 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 29881 | 29723 | 169 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 41561 | 41546 | 25 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 32347 | 32352 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6841 | 6841 | 5678 | 16 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 314 | 314 | 251 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 10418 | 10418 | 10133 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 1 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1995 | 1995 | 1994 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 15638 | 15638 | 14768 | 9 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 482 | 482 | 478 | 4 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 4544 | 4544 | 968 | 44 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1089 | 1089 | 945 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 37 | 37 | 13 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=41574): breakout_not_found=24479, basic_filters_failed=11476, move_not_fresh=3427, breakout_stale=1502, retest_proximity_failed=466, insufficient_candles=153, volume_spike_missing=55, ema_alignment_reject=16
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=35244): cls_disabled_merged_into_lsr=35244
- **EVAL::DIVERGENCE_CONTINUATION** (total=33038): cvd_divergence_failed=13364, basic_filters_failed=8554, h1_trend_not_aligned=5555, ema_alignment_reject=4555, retest_proximity_failed=771, missing_fvg_or_orderblock=239
- **EVAL::FAILED_AUCTION_RECLAIM** (total=33625): auction_not_detected=12747, basic_filters_failed=7898, reclaim_hold_failed=7432, tail_too_small=3777, regime_blocked=1771
- **EVAL::FUNDING_EXTREME** (total=37687): funding_not_extreme=26425, basic_filters_failed=8943, ema_alignment_reject=1038, rsi_reject=1021, momentum_reject=84, missing_fvg_or_orderblock=78, cvd_divergence_failed=68, missing_funding_rate=30
- **EVAL::LIQUIDATION_REVERSAL** (total=32344): cascade_threshold_not_met=22996, basic_filters_failed=8842, cvd_divergence_failed=198, rsi_reject=189, insufficient_candles=92, missing_fvg_or_orderblock=21, volume_spike_missing=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=35366): no_ma_cross=26302, basic_filters_failed=8567, ma_cross_cooldown=467, ma_cross_htf_misaligned=30
- **EVAL::MOVER_AVWAP_SCALP** (total=44689): no_avwap_tag=18046, basic_filters_failed=11411, no_mover_leg=9178, avwap_slope_against=3542, avwap_reclaim_no_volume=1664, insufficient_candles=558, no_avwap_reclaim=290
- **EVAL::MOVER_TREND_PULLBACK** (total=37101): mover_run_too_small=16719, basic_filters_failed=11362, no_reclaim=7086, no_pullback_tag=1377, insufficient_candles=557
- **EVAL::OPENING_RANGE_BREAKOUT** (total=35958): feature_disabled=35958
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=35251): regime_blocked=22897, breakout_not_found=9448, basic_filters_failed=2114, adx_reject=774, ema_alignment_reject=18
- **EVAL::QUIET_COMPRESSION_BREAK** (total=35017): regime_blocked=14076, compression_not_detected=12872, basic_filters_failed=5776, breakout_not_detected=2090, volume_confirmation_failed=187, rsi_reject=14, missing_fvg_or_orderblock=2
- **EVAL::SR_FLIP_RETEST** (total=34044): basic_filters_failed=7883, flip_close_not_confirmed=6076, long_break_volume_thin=4530, long_disabled=4282, whipsaw_flip=3819, reclaim_hold_failed=2540, retest_out_of_zone=2449, regime_blocked=1768, wick_quality_failed=434, long_acceptance_not_held=157, ema_alignment_reject=81, missing_fvg_or_orderblock=25
- **EVAL::STANDARD** (total=27657): momentum_reject=9099, adx_reject=5451, sweeps_not_detected=3663, macd_reject=3294, basic_filters_failed=3170, ema_alignment_reject=2697, invalid_sl_geometry=157, rsi_reject=126
- **EVAL::TREND_PULLBACK** (total=29723): h1_pullback_not_confirmed=7225, h1_trend_not_aligned=6041, ema_alignment_reject=5247, basic_filters_failed=4709, ema_not_tested_prev=2176, no_ema_reclaim_close=1912, body_conviction_fail=1026, rsi_reject=771, prev_already_below_emas=306, prev_already_above_emas=118, no_prev_low_break=105, ema21_not_tagged=30, missing_fvg_or_orderblock=21, momentum_flat=21, no_prev_high_break=9, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=41546): breakout_not_found=21180, basic_filters_failed=11475, move_not_fresh=6027, breakout_stale=1879, retest_proximity_failed=646, insufficient_candles=153, volume_spike_missing=142, missing_fvg_or_orderblock=40, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=32352): momentum_reject=18676, recent_ticks_insufficient=9146, basic_filters_failed=4530

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 69895 | 32.3% |
| QUIET | 57712 | 26.7% |
| TRENDING_UP | 47018 | 21.8% |
| TRENDING_DOWN | 34622 | 16.0% |
| VOLATILE | 6882 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **104**
- Average confidence gap to threshold: **13.05** (samples=104) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SPYUSDT=16, HYPEUSDT=13, TRXUSDT=11, BTCUSDT=10, XLMUSDT=9, SOLUSDT=6, WLDUSDT=5, TRUMPUSDT=5, SOXLUSDT=4, NBISUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 327 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 88 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 103 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 393 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 16 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 23 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 87 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 690 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 4 |
| SR_FLIP_RETEST | filtered | min_confidence | 211 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 57 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 698 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 12 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 93 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 328 | 58.33 | 65.00 | 6.67 | 20.69 | 19.71 | 18.44 | 2.07 | 9.94 |
| DIVERGENCE_CONTINUATION | kept | 88 | 69.96 | 65.00 | -4.96 | 19.80 | 19.84 | 18.05 | 3.49 | 5.44 |
| FAILED_AUCTION_RECLAIM | filtered | 126 | 47.07 | 65.00 | 17.93 | 20.95 | 19.64 | 20.00 | 4.67 | 11.06 |
| FAILED_AUCTION_RECLAIM | kept | 393 | 72.10 | 65.00 | -7.10 | 20.81 | 19.84 | 20.00 | 4.36 | 0.05 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 63.00 | 65.00 | 2.00 | 19.63 | 19.10 | 17.00 | 0.00 | 12.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 64 | 58.38 | 65.00 | 6.62 | 21.46 | 20.00 | 18.15 | 1.19 | 12.54 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 87 | 71.31 | 65.00 | -6.31 | 20.17 | 19.88 | 18.42 | 2.30 | 0.09 |
| MOVER_AVWAP_SCALP | kept | 1 | 81.20 | 65.00 | -16.20 | 16.30 | 19.30 | 15.80 | 3.50 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 690 | 78.68 | 65.00 | -13.68 | 19.38 | 16.75 | 15.80 | 5.13 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 69.12 | 65.00 | -4.12 | 21.42 | 19.70 | 20.00 | 0.00 | 5.20 |
| SR_FLIP_RETEST | filtered | 268 | 56.64 | 65.00 | 8.36 | 21.04 | 19.90 | 15.50 | 1.61 | 13.17 |
| SR_FLIP_RETEST | kept | 698 | 70.31 | 65.00 | -5.31 | 21.15 | 19.92 | 15.56 | 2.10 | -0.54 |
| TREND_PULLBACK_EMA | filtered | 12 | 60.04 | 65.00 | 4.96 | 19.99 | 19.30 | 18.17 | 5.50 | 6.54 |
| TREND_PULLBACK_EMA | kept | 93 | 77.80 | 65.00 | -12.80 | 20.79 | 19.77 | 19.49 | 5.00 | -0.83 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 47.30 | 65.00 | 17.70 | 19.65 | 20.00 | 20.00 | 4.00 | 31.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 328 | 58.33 | 21.20 | 15.56 | 5.09 | 11.70 | 5.41 | 8.21 | 2.07 |
| DIVERGENCE_CONTINUATION | kept | 88 | 69.96 | 24.64 | 17.20 | 4.88 | 11.43 | 5.47 | 8.64 | 3.49 |
| FAILED_AUCTION_RECLAIM | filtered | 126 | 47.07 | 23.06 | 15.71 | 5.36 | 11.08 | 6.05 | 4.74 | 4.67 |
| FAILED_AUCTION_RECLAIM | kept | 393 | 72.10 | 23.00 | 14.52 | 3.18 | 13.42 | 6.55 | 7.16 | 4.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 63.00 | 17.00 | 20.00 | 9.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 64 | 58.38 | 21.88 | 14.75 | 6.52 | 13.48 | 5.03 | 8.08 | 1.19 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 87 | 71.31 | 24.91 | 14.05 | 4.55 | 12.55 | 5.41 | 7.64 | 2.30 |
| MOVER_AVWAP_SCALP | kept | 1 | 81.20 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.70 | 3.50 |
| MOVER_TREND_PULLBACK | kept | 690 | 78.68 | 20.54 | 18.06 | 8.03 | 12.75 | 5.08 | 9.08 | 5.13 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 69.12 | 17.00 | 18.00 | 11.25 | 13.25 | 6.12 | 8.75 | 0.00 |
| SR_FLIP_RETEST | filtered | 268 | 56.64 | 19.77 | 15.87 | 6.21 | 13.41 | 5.90 | 7.04 | 1.61 |
| SR_FLIP_RETEST | kept | 698 | 70.31 | 22.04 | 14.88 | 4.55 | 13.42 | 5.77 | 8.68 | 2.10 |
| TREND_PULLBACK_EMA | filtered | 12 | 60.04 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 8.33 | 5.50 |
| TREND_PULLBACK_EMA | kept | 93 | 77.80 | 22.16 | 18.00 | 7.50 | 13.74 | 5.00 | 9.47 | 5.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 47.30 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 9.30 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 328 | 58.33 | 0.00 | 0.00 | 1.21 | 0.00 | 0.87 | 0.00 | 0.00 | 0.00 | **2.08** |
| DIVERGENCE_CONTINUATION | kept | 88 | 69.96 | 0.00 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.11** |
| FAILED_AUCTION_RECLAIM | filtered | 126 | 47.07 | 0.00 | 0.00 | 1.68 | 0.00 | 2.55 | 0.00 | 0.00 | 0.00 | **4.23** |
| FAILED_AUCTION_RECLAIM | kept | 393 | 72.10 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.04** |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 63.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 64 | 58.38 | 0.00 | 0.00 | 0.90 | 0.00 | 7.76 | 0.00 | 0.00 | 0.00 | **8.66** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 87 | 71.31 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.09** |
| MOVER_AVWAP_SCALP | kept | 1 | 81.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 690 | 78.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 4 | 69.12 | 0.00 | 0.00 | 0.00 | 0.00 | 2.15 | 0.00 | 0.00 | 0.00 | **2.15** |
| SR_FLIP_RETEST | filtered | 268 | 56.64 | 0.00 | 0.00 | 0.90 | 0.00 | 4.22 | 0.00 | 0.00 | 0.72 | **5.84** |
| SR_FLIP_RETEST | kept | 698 | 70.31 | 0.00 | 0.00 | 0.43 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.44** |
| TREND_PULLBACK_EMA | filtered | 12 | 60.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 93 | 77.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 47.30 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=6 (54.5%) | PREMATURE=3 (27.3%) | NEUTRAL=2 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 3 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 6 | 3 | 2 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 0 | 2 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 1 | 0 | 2 | 0 |
| MOVER_AVWAP_SCALP | 2 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 2 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 1 | 1 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 6 | 3 | 2 | 4.4 | 4.2 | +0.02 | **INSUFFICIENT_SAMPLE** — only 11 classified kills (need >= 20); let data accumulate before tuning |

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1384 (30.9%) | WOULD_LOSE=1073 | WOULD_EXPIRE=2018 | pending (awaiting window)=525

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| dispatch_staleness | 1025 | 45.5% | 134.0 | 253.2 | -0.12 | **TUNE** |
| level_still_in_play | 1287 | 25.3% | 118.0 | 203.6 | -0.07 | **TUNE** |
| min_confidence | 1773 | 30.5% | 681.0 | 740.1 | -0.03 | **TUNE** |
| quiet_scalp_block | 232 | 11.2% | 61.0 | 33.7 | +0.12 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 2 | 50.0% | 0.0 | 0.7 | -0.35 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 28 | 35.7% | 18.0 | 7.5 | +0.38 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 74 | 13.5% | 22.0 | 15.4 | +0.09 | **TUNE** |
| shadow_unit:SHADOW_RANGE_FADE | 54 | 11.1% | 39.0 | 12.1 | +0.50 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 7837 across 14 strategies; 170 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 2606 | 4/2602/0 | 38% | -0.27 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+1.11R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 1946 | 0/1946/0 | 49% | -0.00 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.54R) | LONDON/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 1091 | 1/1090/0 | 35% | -0.11 | OVERLAP/ACCUMULATION/EXPANDED/BTC_FALLING (+0.81R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 741 | 0/741/0 | 46% | +0.07 | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL (+0.94R) | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_MEAN_REVERT | 251 | 0/0/251 | 53% | +0.38 | — | — |
| SHADOW_FUNDING_FADE | 240 | 0/0/240 | 32% | -0.44 | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-0.46R) | NY/QUIET/COMPRESSED/BTC_FALLING (-0.87R) |
| LIQUIDITY_SWEEP_REVERSAL | 232 | 0/232/0 | 31% | -0.38 | LONDON/QUIET/NORMAL/BTC_NEUTRAL (+0.18R) | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (-0.85R) |
| QUIET_COMPRESSION_BREAK | 206 | 0/206/0 | 92% | +0.35 | NY/QUIET/NORMAL/BTC_NEUTRAL (+0.52R) | ASIA/QUIET/NORMAL/BTC_FALLING (+0.05R) |
| SHADOW_RANGE_FADE | 182 | 0/0/182 | 37% | -0.04 | — | — |
| TREND_PULLBACK_EMA | 132 | 0/132/0 | 17% | -0.19 | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING (+0.05R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.51R) |
| MOVER_AVWAP_SCALP | 88 | 3/85/0 | 0% | -0.95 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 60 | 0/60/0 | 62% | +0.46 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 53 | 1/52/0 | 2% | -0.64 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 9 | 0/0/9 | 67% | +0.11 | — | — |

- **Strongest cells**: `SR_FLIP_RETEST @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +1.54R (n=23, STRONG); `FUNDING_EXTREME_SIGNAL @ ASIA/ACCUMULATION/NORMAL/BTC_FALLING` +1.24R (n=18, STRONG); `SR_FLIP_RETEST @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.11R (n=50, STRONG)
- **Weakest cells**: `MOVER_TREND_PULLBACK @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL` -1.00R (n=33, NEGATIVE); `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` -1.00R (n=22, NEGATIVE); `VOLUME_SURGE_BREAKOUT @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.00R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._
- _no geometry pairs classified yet — pairs stamp at every post-scoring emission/suppression and classify after ~1h of real candles_

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `55543`
- `Path funnel` emissions: `25`
- `Regime distribution` emissions: `25`
- `QUIET_SCALP_BLOCK` events: `104`
- `confidence_gate` events: `2885`
- `free_channel_post` events: `3`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 3072 | 3072 | 3072 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[present=168421] state[populated=168421] buckets[many=168421] sources[none] quality[none]
- funding_rate: presence[absent=15697, present=152724] state[empty=15697, populated=152724] buckets[few=152724, none=15697] sources[none] quality[none]
- liquidation_clusters: presence[absent=107483, present=60938] state[empty=107483, populated=60938] buckets[few=49048, none=107483, some=11890] sources[none] quality[none]
- oi_snapshot: presence[absent=15697, present=152724] state[empty=15697, populated=152724] buckets[many=151904, none=15697, some=820] sources[none] quality[none]
- order_book: presence[absent=44136, present=124285] state[populated=124285, unavailable=44136] buckets[few=124285, none=44136] sources[book_ticker=124285, unavailable=44136] quality[none=44136, top_of_book_only=124285]
- orderblocks: presence[absent=168421] state[empty=168421] buckets[none=168421] sources[not_implemented=168421] quality[none]
- recent_ticks: presence[present=168421] state[populated=168421] buckets[many=168421] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.0951120853424072` sec
- Median create→first breach: `3352.740044116974` sec
- Median create→terminal: `3354.2611830234528` sec
- Median first breach→terminal: `2.773869037628174` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 11.1}, "under_180s": {"count": 1, "pct": 11.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 11.1}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.4279 | 3352.740044116974 | 3354.2611830234528 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.4884 | 2340.3732744455338 | 2340.771097421646 |
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 40.0 | 0.0 | 0.0 | 0.926 | 3293.165199995041 | 3296.567836046219 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.15 | 8213.134554862976 | 8213.445646047592 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 4544 | 44 | 968 | 0.0 | 0.0 | None | None | 3576 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1089 | 2 | 945 | 0.0 | 0.0 | None | None | 144 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-118`
- Gating Δ: `-136749`
- No-generation Δ: `-1987174`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.6963, "current_avg_pnl": 0.926, "current_win_rate": 0.0, "previous_avg_pnl": 0.2297, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -19, "geometry_changed_delta": 0, "geometry_preserved_delta": -2577, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": -50, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
