# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, LIQUIDITY_SWEEP_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `33` sec (warning=False)
- Latest performance record age: `803` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1284 | 1284 | 1249 | 4 | active-low-quality (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1184 | 1184 | 1124 | 9 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6422 | 6422 | 6221 | 16 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 295905 | 294621 | 1284 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 270528 | 269344 | 1184 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 270528 | 264106 | 6422 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 270528 | 247835 | 22693 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 295905 | 295540 | 365 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 295905 | 295897 | 8 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 270528 | 270516 | 12 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 295905 | 295905 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 270528 | 270508 | 20 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 270528 | 261150 | 9378 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 270528 | 243386 | 27142 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 270528 | 255512 | 15016 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 270528 | 270084 | 444 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 295905 | 294853 | 1052 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 295905 | 295905 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 22693 | 22693 | 17465 | 119 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 365 | 365 | 342 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15016 | 15016 | 12290 | 133 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 20 | 20 | 20 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 9378 | 9378 | 6673 | 129 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 27142 | 27142 | 18191 | 96 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 444 | 444 | 426 | 5 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1052 | 1052 | 1032 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=294621): breakout_not_found=141041, basic_filters_failed=85438, retest_proximity_failed=55010, volume_spike_missing=8279, insufficient_candles=2732, ema_alignment_reject=1470, missing_fvg_or_orderblock=651
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=269344): regime_blocked=191450, sweeps_not_detected=37655, basic_filters_failed=16544, ema_alignment_reject=11072, adx_reject=6296, momentum_reject=4992, reclaim_confirmation_failed=1325, rsi_reject=10
- **EVAL::DIVERGENCE_CONTINUATION** (total=264106): regime_blocked=191450, cvd_divergence_failed=49073, basic_filters_failed=16544, ema_alignment_reject=5383, retest_proximity_failed=1043, missing_fvg_or_orderblock=613
- **EVAL::FAILED_AUCTION_RECLAIM** (total=247835): auction_not_detected=101499, basic_filters_failed=76237, reclaim_hold_failed=44994, tail_too_small=25022, rsi_reject=83
- **EVAL::FUNDING_EXTREME** (total=295540): funding_not_extreme=201400, basic_filters_failed=85126, missing_funding_rate=3665, ema_alignment_reject=3073, rsi_reject=1333, cvd_divergence_failed=329, momentum_reject=284, insufficient_candles=272, missing_fvg_or_orderblock=58
- **EVAL::LIQUIDATION_REVERSAL** (total=295897): cascade_threshold_not_met=206255, basic_filters_failed=85763, insufficient_candles=1931, cvd_divergence_failed=986, rsi_reject=825, missing_fvg_or_orderblock=98, volume_spike_missing=39
- **EVAL::MA_CROSS_TREND_SHIFT** (total=270516): no_ma_cross=191975, basic_filters_failed=76237, ma_cross_cooldown=2304
- **EVAL::OPENING_RANGE_BREAKOUT** (total=295905): feature_disabled=295905
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=270508): regime_blocked=191450, breakout_not_found=45146, basic_filters_failed=16544, ema_alignment_reject=11072, adx_reject=6296
- **EVAL::QUIET_COMPRESSION_BREAK** (total=261150): breakout_not_detected=100409, regime_blocked=79078, basic_filters_failed=59693, compression_not_detected=19591, rsi_reject=1538, missing_fvg_or_orderblock=841
- **EVAL::SR_FLIP_RETEST** (total=243386): basic_filters_failed=76237, reclaim_hold_failed=59802, flip_close_not_confirmed=57851, retest_out_of_zone=34918, wick_quality_failed=10571, missing_fvg_or_orderblock=2252, ema_alignment_reject=1073, rsi_reject=682
- **EVAL::STANDARD** (total=255512): momentum_reject=57460, sweeps_not_detected=54821, basic_filters_failed=54816, adx_reject=49227, macd_reject=24008, ema_alignment_reject=14004, invalid_sl_geometry=735, rsi_reject=392, mtf_reject=37, htf_ema_reject=12
- **EVAL::TREND_PULLBACK** (total=270084): regime_blocked=191450, ema_not_tested_prev=20831, basic_filters_failed=16544, ema_alignment_reject=15217, rsi_reject=8275, body_conviction_fail=8007, no_ema_reclaim_close=7981, prev_already_below_emas=766, no_prev_low_break=553, prev_already_above_emas=138, momentum_flat=130, no_prev_high_break=91, momentum_reject=39, ema21_not_tagged=38, missing_fvg_or_orderblock=24
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=294853): breakout_not_found=174600, basic_filters_failed=85438, retest_proximity_failed=23088, volume_spike_missing=5456, ema_alignment_reject=2738, insufficient_candles=2732, missing_fvg_or_orderblock=771, rsi_reject=30
- **EVAL::WHALE_MOMENTUM** (total=295905): momentum_reject=204741, recent_ticks_insufficient=67643, basic_filters_failed=23521

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 255519 | 69.9% |
| TRENDING_DOWN | 90568 | 24.8% |
| TRENDING_UP | 14083 | 3.9% |
| RANGING | 5170 | 1.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1841**
- Average confidence gap to threshold: **16.27** (samples=1841) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HYPEUSDT=108, ZECUSDT=94, CLUSDT=86, ORCAUSDT=68, AAVEUSDT=63, MUUSDT=57, SUIUSDT=55, INJUSDT=48, AVAXUSDT=47, ETCUSDT=46

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 6 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 10 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 11 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 11 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 35 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 317 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 117 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1170 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 374 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 12 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 559 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 726 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 995 |
| SR_FLIP_RETEST | filtered | min_confidence | 504 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 424 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 774 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 11 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 3 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 63.05 | 65.00 | 1.95 | 19.95 | 19.30 | 18.70 | 0.00 | 5.50 |
| BREAKDOWN_SHORT | kept | 6 | 68.67 | 65.00 | -3.67 | 20.52 | 19.15 | 19.25 | 0.00 | 2.30 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 10 | 58.22 | 65.00 | 6.78 | 20.35 | 19.08 | 17.00 | 1.00 | 1.76 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 11 | 71.46 | 65.00 | -6.46 | 20.75 | 19.72 | 17.00 | 1.09 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 11 | 51.95 | 65.00 | 13.05 | 20.74 | 19.94 | 17.05 | 0.45 | 1.80 |
| DIVERGENCE_CONTINUATION | kept | 35 | 70.63 | 65.00 | -5.63 | 20.31 | 19.63 | 17.72 | 1.29 | -1.18 |
| FAILED_AUCTION_RECLAIM | filtered | 434 | 49.48 | 65.00 | 15.52 | 20.65 | 19.49 | 14.00 | 4.39 | 11.87 |
| FAILED_AUCTION_RECLAIM | kept | 1170 | 71.00 | 65.00 | -6.00 | 20.61 | 19.72 | 14.00 | 4.39 | 0.35 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 47.30 | 65.00 | 17.70 | 18.10 | 20.00 | 17.00 | 2.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 386 | 48.94 | 65.00 | 16.06 | 20.90 | 19.60 | 15.20 | 2.52 | 13.24 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 559 | 70.03 | 65.00 | -5.03 | 20.94 | 19.65 | 15.20 | 2.90 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 733 | 50.96 | 65.00 | 14.04 | 21.07 | 19.22 | 15.80 | 0.00 | 7.02 |
| QUIET_COMPRESSION_BREAK | kept | 995 | 73.64 | 65.00 | -8.64 | 20.24 | 19.68 | 15.80 | 0.00 | -0.27 |
| SR_FLIP_RETEST | filtered | 928 | 50.16 | 65.00 | 14.84 | 20.16 | 19.93 | 15.95 | 1.81 | 11.01 |
| SR_FLIP_RETEST | kept | 774 | 70.09 | 65.00 | -5.09 | 20.03 | 19.97 | 15.75 | 2.16 | -1.15 |
| TREND_PULLBACK_EMA | kept | 11 | 76.80 | 65.00 | -11.80 | 21.08 | 19.88 | 18.32 | 5.50 | -1.36 |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 63.00 | 65.00 | 2.00 | 20.60 | 19.60 | 20.00 | 4.00 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.15 | 65.00 | -4.15 | 20.30 | 19.35 | 20.00 | 3.00 | 1.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 63.05 | 21.00 | 18.00 | 3.00 | 13.50 | 6.75 | 6.30 | 0.00 |
| BREAKDOWN_SHORT | kept | 6 | 68.67 | 22.33 | 18.00 | 5.50 | 12.33 | 4.58 | 8.22 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 10 | 58.22 | 19.20 | 18.00 | 6.30 | 12.00 | 5.60 | 7.48 | 1.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 11 | 71.46 | 21.36 | 18.00 | 4.09 | 13.09 | 6.41 | 8.51 | 1.09 |
| DIVERGENCE_CONTINUATION | filtered | 11 | 51.95 | 24.27 | 18.00 | 5.73 | 11.00 | 5.27 | 4.03 | 0.45 |
| DIVERGENCE_CONTINUATION | kept | 35 | 70.63 | 20.66 | 18.00 | 5.66 | 12.03 | 5.00 | 8.53 | 1.29 |
| FAILED_AUCTION_RECLAIM | filtered | 434 | 49.48 | 21.55 | 14.18 | 6.86 | 11.26 | 6.86 | 5.59 | 4.39 |
| FAILED_AUCTION_RECLAIM | kept | 1170 | 71.00 | 22.96 | 14.08 | 4.84 | 11.59 | 5.84 | 7.66 | 4.39 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 47.30 | 25.00 | 8.00 | 6.00 | 14.00 | 5.00 | 7.30 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 386 | 48.94 | 22.56 | 14.02 | 7.16 | 12.56 | 5.40 | 5.62 | 2.52 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 559 | 70.03 | 23.79 | 14.11 | 4.11 | 12.02 | 5.83 | 7.26 | 2.90 |
| QUIET_COMPRESSION_BREAK | filtered | 733 | 50.96 | 19.11 | 17.90 | 9.50 | 14.52 | 6.79 | 3.38 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 995 | 73.64 | 18.78 | 17.87 | 8.09 | 14.27 | 6.90 | 8.66 | 0.00 |
| SR_FLIP_RETEST | filtered | 928 | 50.16 | 20.28 | 13.43 | 7.73 | 13.90 | 6.65 | 6.18 | 1.81 |
| SR_FLIP_RETEST | kept | 774 | 70.09 | 22.25 | 12.95 | 5.17 | 13.82 | 6.06 | 8.80 | 2.16 |
| TREND_PULLBACK_EMA | kept | 11 | 76.80 | 19.91 | 18.00 | 4.36 | 14.00 | 6.09 | 8.94 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 63.00 | 25.00 | 8.00 | 6.00 | 10.00 | 5.00 | 8.00 | 4.00 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.15 | 25.00 | 13.00 | 3.00 | 12.00 | 6.50 | 8.15 | 3.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 63.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 6 | 68.67 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | **0.80** |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 10 | 58.22 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **0.96** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 11 | 71.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 11 | 51.95 | 0.00 | 0.00 | 3.05 | 0.00 | 0.65 | 0.00 | **3.70** |
| DIVERGENCE_CONTINUATION | kept | 35 | 70.63 | 0.00 | 0.00 | 0.14 | 0.00 | 0.82 | 0.00 | **0.96** |
| FAILED_AUCTION_RECLAIM | filtered | 434 | 49.48 | 0.00 | 0.00 | 2.33 | 0.00 | 8.11 | 0.08 | **10.52** |
| FAILED_AUCTION_RECLAIM | kept | 1170 | 71.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.15 | 0.00 | **0.16** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 47.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 386 | 48.94 | 0.00 | 0.00 | 3.66 | 0.00 | 9.60 | 0.00 | **13.26** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 559 | 70.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 733 | 50.96 | 0.00 | 0.00 | 1.63 | 0.00 | 2.47 | 0.00 | **4.10** |
| QUIET_COMPRESSION_BREAK | kept | 995 | 73.64 | 0.00 | 0.00 | 0.04 | 0.00 | 1.66 | 0.00 | **1.70** |
| SR_FLIP_RETEST | filtered | 928 | 50.16 | 0.01 | 0.00 | 0.75 | 0.00 | 6.93 | 0.01 | **7.70** |
| SR_FLIP_RETEST | kept | 774 | 70.09 | 0.00 | 0.00 | 0.12 | 0.00 | 0.09 | 0.01 | **0.22** |
| TREND_PULLBACK_EMA | kept | 11 | 76.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 63.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=68 (56.7%) | PREMATURE=9 (7.5%) | NEUTRAL=43 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 59 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 4 | 0 | 0 | 0 |
| other | 42 | 4 | 14 | 0 |
| regime_shift | 22 | 5 | 29 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 0 | 0 | 0 |
| CONTINUATION_LIQUIDITY_SWEEP | 2 | 0 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 4 | 0 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 11 | 1 | 5 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 20 | 5 | 14 | 0 |
| QUIET_COMPRESSION_BREAK | 17 | 1 | 14 | 0 |
| SR_FLIP_RETEST | 13 | 2 | 8 | 0 |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1974293`
- `Path funnel` emissions: `51`
- `Regime distribution` emissions: `51`
- `QUIET_SCALP_BLOCK` events: `1841`
- `confidence_gate` events: `6071`
- `free_channel_post` events: `259`
- `pre_tp_fire` events: `146`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **146**
- Avg resolved threshold: **0.334%** raw → avg net **+2.64%** @ 10x
- Avg time-to-fire from dispatch: **379s**
- By threshold source: stamped=146

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 50 | 0.389% | +3.19% | 334 | stamped=50 |
| SR_FLIP_RETEST | 33 | 0.295% | +2.25% | 415 | stamped=33 |
| QUIET_COMPRESSION_BREAK | 30 | 0.245% | +1.75% | 304 | stamped=30 |
| FAILED_AUCTION_RECLAIM | 20 | 0.374% | +3.04% | 403 | stamped=20 |
| DIVERGENCE_CONTINUATION | 9 | 0.348% | +2.78% | 562 | stamped=9 |
| TREND_PULLBACK_EMA | 3 | 0.458% | +3.88% | 654 | stamped=3 |
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 0.231% | +1.61% | 803 | stamped=1 |
- Top symbols: GUAUSDT=8, GWEIUSDT=7, FFUSDT=6, ARCUSDT=6, RIVERUSDT=6, DOGEUSDT=5, SOLUSDT=5, SUIUSDT=5, ICPUSDT=5, CHZUSDT=5

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 6 | 3247 | 26532 | 28125 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **259**

| Source | Count |
|---|---:|
| pre_tp | 146 |
| signal_close | 110 |
| signal_highlight | 2 |
| regime_shift | 1 |

- By severity: HIGH=259

## Dependency readiness
- cvd: presence[present=295905] state[populated=295905] buckets[few=49, many=295642, some=214] sources[none] quality[none]
- funding_rate: presence[absent=3665, present=292240] state[empty=3665, populated=292240] buckets[few=292240, none=3665] sources[none] quality[none]
- liquidation_clusters: presence[absent=171895, present=124010] state[empty=171895, populated=124010] buckets[few=101795, none=171895, some=22215] sources[none] quality[none]
- oi_snapshot: presence[absent=1152, present=294753] state[empty=1152, populated=294753] buckets[few=382, many=292050, none=1152, some=2321] sources[none] quality[none]
- order_book: presence[absent=77112, present=218793] state[populated=218793, unavailable=77112] buckets[few=218793, none=77112] sources[book_ticker=218793, unavailable=77112] quality[none=77112, top_of_book_only=218793]
- orderblocks: presence[absent=295905] state[empty=295905] buckets[none=295905] sources[not_implemented=295905] quality[none]
- recent_ticks: presence[absent=3066, present=292839] state[empty=3066, populated=292839] buckets[many=292839, none=3066] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.019877910614014` sec
- Median create→first breach: `435.9180819988251` sec
- Median create→terminal: `745.803111076355` sec
- Median first breach→terminal: `5.066541910171509` sec
- Fast-failure buckets: `{"under_120s": {"count": 16, "pct": 15.2}, "under_180s": {"count": 21, "pct": 20.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 8, "pct": 7.6}}`
- ~3 minute terminal-close behavior: `{"count": 11, "pct": 4.1}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 66.7 | 0.0 | -0.7659 | 754.4791150093079 | 734.0714638233185 |
| CONTINUATION_LIQUIDITY_SWEEP | 6 | 6 | 0.0 | 16.7 | 0.0 | -0.1273 | 829.5595669746399 | 1441.9066804647446 |
| DIVERGENCE_CONTINUATION | 16 | 16 | 0.0 | 18.8 | 0.0 | 0.0776 | 742.4473860263824 | 771.4058924913406 |
| FAILED_AUCTION_RECLAIM | 42 | 42 | 0.0 | 11.9 | 0.0 | -0.1083 | 449.7983355522156 | 656.7495291233063 |
| LIQUIDITY_SWEEP_REVERSAL | 91 | 91 | 0.0 | 8.8 | 0.0 | 0.048 | 388.3302948474884 | 714.5963640213013 |
| QUIET_COMPRESSION_BREAK | 59 | 59 | 0.0 | 0.0 | 0.0 | 0.0112 | 372.2957248687744 | 760.4507789611816 |
| SR_FLIP_RETEST | 57 | 57 | 0.0 | 5.3 | 0.0 | 0.1137 | 428.7093563079834 | 921.021810054779 |
| TREND_PULLBACK_EMA | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.141 | 376.8009970188141 | 483.3690469264984 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.2408 | None | 1098.0927171707153 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 27142 | 96 | 18191 | 0.0 | 5.3 | 428.7093563079834 | 921.021810054779 | 8951 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 444 | 5 | 426 | 0.0 | 33.3 | 376.8009970188141 | 483.3690469264984 | 18 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `60`
- Gating Δ: `2265`
- No-generation Δ: `377463`
- Fast failures Δ: `21`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.7659, "current_avg_pnl": -0.7659, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "CONTINUATION_LIQUIDITY_SWEEP": {"avg_pnl_delta": -0.1273, "current_avg_pnl": -0.1273, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0776, "current_avg_pnl": 0.0776, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1083, "current_avg_pnl": -0.1083, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.048, "current_avg_pnl": 0.048, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0112, "current_avg_pnl": 0.0112, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1137, "current_avg_pnl": 0.1137, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.141, "current_avg_pnl": 0.141, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -35, "geometry_changed_delta": 0, "geometry_preserved_delta": 1790, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 428.71, "median_terminal_delta_sec": 921.02, "sl_rate_delta": 5.3, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -33, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 376.8, "median_terminal_delta_sec": 483.37, "sl_rate_delta": 33.3, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
