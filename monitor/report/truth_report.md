# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::BREAKDOWN_SHORT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `2813` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 2439 | 2439 | 2221 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 13279 | 13282 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 11926 | 11929 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 11901 | 11387 | 541 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 11931 | 11442 | 510 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 12272 | 12263 | 10 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 10985 | 10985 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 11953 | 11956 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 11956 | 11701 | 313 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 13561 | 14101 | 45 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 13282 | 12200 | 1361 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 11743 | 11744 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 11930 | 11931 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 11899 | 11790 | 111 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 12014 | 12017 | 0 | 0 | 0 | 0 | non-generating (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 11370 | 10985 | 913 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 10567 | 10115 | 490 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 10606 | 10540 | 71 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 13276 | 13273 | 5 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 10985 | 10965 | 26 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1930 | 1930 | 1106 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 45 | 45 | 44 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 2989 | 2989 | 2975 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 717 | 717 | 717 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 95 | 95 | 94 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 3194 | 3194 | 1387 | 10 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 308 | 308 | 68 | 16 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 2456 | 2456 | 1387 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 224 | 224 | 198 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 90 | 90 | 19 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 799 | 799 | 799 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=13282): breakout_not_found=5968, basic_filters_failed=4166, move_not_fresh=2197, breakout_stale=842, retest_proximity_failed=95, volume_spike_missing=14
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=11929): cls_disabled_merged_into_lsr=11929
- **EVAL::DIVERGENCE_CONTINUATION** (total=11387): cvd_divergence_failed=4250, basic_filters_failed=3191, h1_trend_not_aligned=2741, ema_alignment_reject=1037, missing_fvg_or_orderblock=90, retest_proximity_failed=78
- **EVAL::FAILED_AUCTION_RECLAIM** (total=11442): auction_not_detected=3813, reclaim_hold_failed=3259, basic_filters_failed=3176, tail_too_small=1032, regime_blocked=162
- **EVAL::FUNDING_EXTREME** (total=12263): funding_not_extreme=8430, basic_filters_failed=3429, missing_funding_rate=159, rsi_reject=129, ema_alignment_reject=78, momentum_reject=20, cvd_divergence_failed=17, missing_fvg_or_orderblock=1
- **EVAL::LIQUIDATION_REVERSAL** (total=10985): cascade_threshold_not_met=7468, basic_filters_failed=3452, rsi_reject=34, cvd_divergence_failed=29, missing_fvg_or_orderblock=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=11956): no_ma_cross=8744, basic_filters_failed=3191, ma_cross_cooldown=17, ma_cross_htf_misaligned=4
- **EVAL::MEAN_REVERT** (total=11701): no_extension=9599, basic_filters_failed=2102
- **EVAL::MOVER_AVWAP_SCALP** (total=14101): no_mover_leg=4807, basic_filters_failed=4171, no_avwap_tag=3125, avwap_slope_against=1414, avwap_reclaim_no_volume=484, no_avwap_reclaim=79, anchor_too_recent=21
- **EVAL::MOVER_TREND_PULLBACK** (total=12200): mover_run_too_small=6058, basic_filters_failed=4169, no_reclaim=1595, no_pullback_tag=378
- **EVAL::OPENING_RANGE_BREAKOUT** (total=11744): feature_disabled=11744
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=11931): regime_blocked=7115, breakout_not_found=3199, basic_filters_failed=965, adx_reject=647, ema_alignment_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=11790): regime_blocked=4970, compression_not_detected=2596, basic_filters_failed=2211, breakout_not_detected=1809, volume_confirmation_failed=197, rsi_reject=5, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=12017): no_range_edge=9915, basic_filters_failed=2102
- **EVAL::SR_FLIP_RETEST** (total=10985): basic_filters_failed=3176, whipsaw_flip=1553, long_disabled=1393, long_break_volume_thin=1381, reclaim_hold_failed=1196, flip_close_not_confirmed=1127, retest_out_of_zone=500, wick_quality_failed=288, regime_blocked=162, missing_fvg_or_orderblock=102, long_acceptance_not_held=93, ema_alignment_reject=14
- **EVAL::STANDARD** (total=10115): momentum_reject=3658, adx_reject=2510, basic_filters_failed=1354, sweeps_not_detected=1082, macd_reject=964, ema_alignment_reject=525, invalid_sl_geometry=12, rsi_reject=10
- **EVAL::TREND_PULLBACK** (total=10540): h1_trend_not_aligned=3293, basic_filters_failed=1970, ema_alignment_reject=1890, h1_pullback_not_confirmed=873, ema_not_tested_prev=694, body_conviction_fail=632, rsi_reject=549, no_ema_reclaim_close=317, prev_already_above_emas=237, no_prev_low_break=41, momentum_flat=16, no_prev_high_break=14, prev_already_below_emas=9, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=13273): breakout_not_found=7126, basic_filters_failed=4165, move_not_fresh=1316, breakout_stale=480, retest_proximity_failed=175, volume_spike_missing=6, ema_alignment_reject=4, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=10965): momentum_reject=7708, recent_ticks_insufficient=2407, basic_filters_failed=850

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=99): setup_compat:regime_VOLATILE_UNSUITABLE=50, context_floor=49
- **FAILED_AUCTION_RECLAIM** (total=618): context_floor=424, setup_compat:regime_STRONG_TREND=158, execution:overextended=36
- **FUNDING_EXTREME_SIGNAL** (total=44): execution:trigger_not_confirmed=44
- **LIQUIDITY_SWEEP_REVERSAL** (total=623): execution:trigger_not_confirmed=427, execution:overextended=109, setup_compat:regime_STRONG_TREND=84, context_floor=3
- **MOVER_AVWAP_SCALP** (total=77): execution:overextended=47, execution:trigger_not_confirmed=30
- **MOVER_TREND_PULLBACK** (total=1632): execution:trigger_not_confirmed=897, execution:overextended=384, context_floor=351
- **QUIET_COMPRESSION_BREAK** (total=8): execution:trigger_not_confirmed=8
- **SR_FLIP_RETEST** (total=305): context_floor=305
- **TREND_PULLBACK_EMA** (total=177): setup_compat:regime_CLEAN_RANGE=146, setup_compat:regime_DIRTY_RANGE=11, context_floor=11, setup_compat:regime_VOLATILE_UNSUITABLE=9
- **WHALE_MOMENTUM** (total=799): execution:trigger_not_confirmed=799

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 23050 | 33.7% |
| QUIET | 17269 | 25.2% |
| TRENDING_UP | 13999 | 20.5% |
| TRENDING_DOWN | 11342 | 16.6% |
| VOLATILE | 2788 | 4.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **40**
- Average confidence gap to threshold: **11.08** (samples=40) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: VIRTUALUSDT=12, BCHUSDT=11, FILUSDT=6, CHZUSDT=5, 1000SHIBUSDT=3, DOTUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 4 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 35 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 42 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 211 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 11 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 929 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 11 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 229 |
| SR_FLIP_RETEST | filtered | min_confidence | 30 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 112 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 51.78 | 65.00 | 13.22 | 20.96 | 19.76 | 16.48 | 2.00 | 8.52 |
| FAILED_AUCTION_RECLAIM | filtered | 52 | 54.95 | 62.38 | 7.43 | 22.00 | 19.95 | 20.00 | 4.30 | 5.24 |
| FAILED_AUCTION_RECLAIM | kept | 42 | 70.33 | 65.00 | -5.33 | 21.08 | 17.81 | 20.00 | 4.21 | 0.12 |
| MOVER_AVWAP_SCALP | kept | 1 | 70.20 | 65.00 | -5.20 | 21.00 | 16.90 | 15.80 | 4.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 222 | 55.02 | 60.46 | 5.44 | 22.28 | 19.66 | 15.80 | 4.03 | 19.06 |
| MOVER_TREND_PULLBACK | kept | 929 | 75.53 | 65.00 | -10.53 | 20.36 | 19.51 | 15.80 | 4.63 | 2.77 |
| QUIET_COMPRESSION_BREAK | filtered | 11 | 47.47 | 65.00 | 17.53 | 22.52 | 19.85 | 20.00 | 0.00 | 29.35 |
| QUIET_COMPRESSION_BREAK | kept | 229 | 75.67 | 65.00 | -10.67 | 21.93 | 19.62 | 20.00 | 0.00 | 0.42 |
| SR_FLIP_RETEST | filtered | 30 | 41.72 | 60.13 | 18.41 | 17.65 | 19.74 | 15.20 | 1.70 | 28.98 |
| SR_FLIP_RETEST | kept | 112 | 69.01 | 65.00 | -4.01 | 21.29 | 20.00 | 16.08 | 1.65 | -0.22 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 51.78 | 23.40 | 8.00 | 6.60 | 15.20 | 4.70 | 7.60 | 2.00 |
| FAILED_AUCTION_RECLAIM | filtered | 52 | 54.95 | 21.65 | 14.00 | 5.37 | 11.60 | 7.92 | 5.16 | 4.30 |
| FAILED_AUCTION_RECLAIM | kept | 42 | 70.33 | 20.76 | 17.05 | 5.07 | 11.29 | 6.98 | 5.45 | 4.21 |
| MOVER_AVWAP_SCALP | kept | 1 | 70.20 | 15.00 | 18.00 | 7.50 | 14.00 | 5.00 | 6.70 | 4.00 |
| MOVER_TREND_PULLBACK | filtered | 222 | 55.02 | 17.49 | 18.00 | 8.48 | 11.19 | 5.56 | 9.80 | 4.03 |
| MOVER_TREND_PULLBACK | kept | 929 | 75.53 | 19.53 | 18.00 | 8.43 | 12.64 | 5.82 | 9.71 | 4.63 |
| QUIET_COMPRESSION_BREAK | filtered | 11 | 47.47 | 17.73 | 18.00 | 11.73 | 14.00 | 7.36 | 8.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 229 | 75.67 | 18.65 | 16.72 | 11.99 | 14.01 | 6.15 | 9.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 30 | 41.72 | 20.73 | 18.00 | 6.00 | 11.00 | 5.00 | 8.27 | 1.70 |
| SR_FLIP_RETEST | kept | 112 | 69.01 | 20.43 | 17.91 | 3.80 | 10.93 | 5.19 | 9.76 | 1.65 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 51.78 | 0.00 | 0.00 | 0.00 | 0.00 | 4.32 | 0.00 | 0.00 | 0.00 | **4.32** |
| FAILED_AUCTION_RECLAIM | filtered | 52 | 54.95 | 0.00 | 0.00 | 0.00 | 0.00 | 4.57 | 0.00 | 0.00 | 0.00 | **4.57** |
| FAILED_AUCTION_RECLAIM | kept | 42 | 70.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 1 | 70.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 222 | 55.02 | 0.00 | 0.00 | 0.00 | 0.00 | 2.85 | 0.40 | 0.00 | 0.00 | **3.25** |
| MOVER_TREND_PULLBACK | kept | 929 | 75.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.89 | 0.06 | 0.00 | 0.00 | **0.95** |
| QUIET_COMPRESSION_BREAK | filtered | 11 | 47.47 | 27.00 | 0.00 | 0.00 | 0.00 | 2.35 | 0.00 | 0.00 | 0.00 | **29.35** |
| QUIET_COMPRESSION_BREAK | kept | 229 | 75.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.87 | 0.00 | 0.00 | 0.00 | **0.87** |
| SR_FLIP_RETEST | filtered | 30 | 41.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.33 | 0.00 | 0.00 | **1.33** |
| SR_FLIP_RETEST | kept | 112 | 69.01 | 0.00 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.43** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=668 (17.7%) | WOULD_LOSE=1064 | WOULD_EXPIRE=2046 | pending (awaiting window)=1153

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 73 | 9.6% | 33.0 | 10.1 | +0.31 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 998 | 6.7% | 13.0 | 134.0 | -0.12 | **TUNE** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 11 | 0.0% | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** |
| context_floor:MEAN_REVERT | 98 | 0.0% | 98.0 | 0.0 | +1.00 | **KEEP** |
| context_floor:MOVER_TREND_PULLBACK | 746 | 8.4% | 289.0 | 82.7 | +0.28 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 71 | 0.0% | 0.0 | 0.0 | +0.00 | **TUNE** |
| context_floor:SR_FLIP_RETEST | 413 | 18.2% | 304.0 | 94.8 | +0.51 | **KEEP** |
| context_floor:TREND_PULLBACK_EMA | 11 | 0.0% | 11.0 | 0.0 | +1.00 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 44 | 22.7% | 0.0 | 3.5 | -0.08 | **TUNE** |
| dispatch_staleness | 441 | 70.3% | 55.0 | 251.3 | -0.45 | **DROP** |
| level_still_in_play | 296 | 20.6% | 4.0 | 38.8 | -0.12 | **TUNE** |
| min_confidence | 322 | 6.5% | 156.0 | 31.9 | +0.39 | **KEEP** |
| quiet_scalp_block | 104 | 4.8% | 12.0 | 6.0 | +0.06 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 4 | 25.0% | 2.0 | 0.8 | +0.31 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 37 | 21.6% | 29.0 | 6.0 | +0.62 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 56 | 12.5% | 48.0 | 12.1 | +0.64 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 53 | 62.3% | 10.0 | 118.2 | -2.04 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 39721 across 20 strategies; 898 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 10169 | 27/10142/0 | 63% | +0.23 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 7206 | 2/7204/0 | 42% | -0.10 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+1.18R) | LONDON/MARKDOWN/EXPANDED/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 6744 | 14/6730/0 | 56% | +0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.86R) | LONDON/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| DIVERGENCE_CONTINUATION | 3790 | 5/3785/0 | 45% | +0.03 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.00R) |
| QUIET_COMPRESSION_BREAK | 2720 | 0/2720/0 | 47% | +0.08 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 2103 | 0/0/2103 | 33% | -0.15 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 1880 | 0/0/1880 | 37% | +0.21 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.78R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 1482 | 1/1481/0 | 32% | -0.18 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 1104 | 0/0/1104 | 33% | -0.42 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 584 | 6/578/0 | 31% | -0.24 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 443 | 0/443/0 | 36% | -0.18 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.27R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| MEAN_REVERT | 439 | 0/439/0 | 7% | -0.91 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+0.15R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 232 | 0/232/0 | 54% | -0.06 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 208 | 0/208/0 | 39% | -0.03 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| BREAKDOWN_SHORT | 201 | 1/200/0 | 62% | +0.45 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| MOVER_AVWAP_SCALP | 191 | 6/185/0 | 20% | -0.61 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 156 | 0/0/156 | 46% | -0.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.20R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| RANGE_FADE | 60 | 0/60/0 | 100% | +4.76 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG)
- **Weakest cells**: `SR_FLIP_RETEST @ ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.00R (n=24, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.00R (n=50, NEGATIVE); `MEAN_REVERT @ NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.00R (n=42, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_AVWAP_SCALP | 32 | 38% / -0.19R | 32 | 47% / -0.03R | +0.16 | **ATR** |
| TREND_PULLBACK_EMA | 15 | 60% / -0.01R | 15 | 67% / +0.15R | +0.16 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 19 | 42% / +0.01R | 19 | 37% / -0.10R | -0.11 | **FIXED** |
| WHALE_MOMENTUM | 17 | 29% / -0.23R | 17 | 24% / -0.31R | -0.08 | **FIXED** |
| SR_FLIP_RETEST | 1003 | 45% / -0.07R | 1003 | 49% / -0.01R | +0.06 | **ATR** |
| FAILED_AUCTION_RECLAIM | 827 | 50% / +0.02R | 827 | 49% / +0.06R | +0.04 | **ATR** |
| MEAN_REVERT | 35 | 9% / -0.88R | 35 | 6% / -0.91R | -0.03 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 155 | 45% / -0.07R | 155 | 50% / -0.05R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 444 | 45% / +0.01R | 444 | 44% / +0.01R | +0.01 | **ATR** |
| DIVERGENCE_CONTINUATION | 183 | 49% / -0.01R | 183 | 55% / -0.02R | -0.00 | **FIXED** |
| MOVER_TREND_PULLBACK | 775 | 62% / +0.13R | 775 | 66% / +0.13R | +0.00 | **ATR** |
| BREAKDOWN_SHORT | 7 | 29% / -0.27R | 7 | 29% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 2 | 0% / -1.00R | 2 | 100% / +0.22R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0% / +0.00R | 1 | 0% / +0.00R | — | **MEASURING** |
| RANGE_FADE | 3 | 100% / +4.79R | 3 | 100% / +3.83R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 15 · alerting: **1** · boot grace active: False
- **ALERT** `mean_revert_emission` — 717 detections since last emission (emitted_total=0) — check gate rejections (streak 17/6) (sustained 17 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=1 fanouts=1 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 65511.90 | 0 |
| candle_coverage | ok | 93/96 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +41 / upstream +37 | 0 |
| emission_controller | ok | last cycle 1223s ago; live_overrides=2 | 0 |
| geometry_ab | ok | output +2 / upstream +41 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 717 detections since last emission (emitted_total=0) — check gate rejections (streak 17/6) | 17 |
| mean_revert_path | ok | output +37 / upstream +41 | 0 |
| range_fade_emission | ok | backlog 0 detections since last progress | 0 |
| range_fade_path | violating | upstream +41 but output +0 (streak 17/72) | 17 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| strategy_edge | ok | output +207 / upstream +41 | 0 |
| suppression_audit | ok | output +41 / upstream +37 | 0 |
| tuned_variants | ok | seen=1 stamped=0 skipped=0 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `25508`
- `Path funnel` emissions: `8`
- `Regime distribution` emissions: `8`
- `QUIET_SCALP_BLOCK` events: `40`
- `confidence_gate` events: `1633`
- `free_channel_post` events: `1`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **1**

| Source | Count |
|---|---:|
| signal_close | 1 |

- By severity: HIGH=1

## Dependency readiness
- cvd: presence[present=49541] state[populated=49541] buckets[many=49541] sources[none] quality[none]
- funding_rate: presence[absent=4745, present=44796] state[empty=4745, populated=44796] buckets[few=44796, none=4745] sources[none] quality[none]
- liquidation_clusters: presence[absent=31074, present=18467] state[empty=31074, populated=18467] buckets[few=15130, none=31074, some=3337] sources[none] quality[none]
- oi_snapshot: presence[absent=4210, present=45331] state[empty=4210, populated=45331] buckets[many=45331, none=4210] sources[none] quality[none]
- order_book: presence[absent=13721, present=35820] state[populated=35820, unavailable=13721] buckets[few=35820, none=13721] sources[book_ticker=35820, unavailable=13721] quality[none=13721, top_of_book_only=35820]
- orderblocks: presence[absent=49541] state[empty=49541] buckets[none=49541] sources[not_implemented=49541] quality[none]
- recent_ticks: presence[present=49541] state[populated=49541] buckets[many=49541] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.879413604736328` sec
- Median create→first breach: `2107.992952466011` sec
- Median create→terminal: `2234.3265665769577` sec
- Median first breach→terminal: `0.8658500909805298` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0945 | 955.5695118904114 | 955.982095003128 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.4855 | 2003.1093089580536 | 2004.9683470726013 |
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 80.0 | 0.0 | 0.0 | -1.3128 | 2212.8765959739685 | 2463.684786081314 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.0244 | 9530.649816036224 | 9532.028242111206 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.5748 | 2950.6847945451736 | 2951.4363169670105 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 2456 | 4 | 1387 | 100.0 | 0.0 | 9530.649816036224 | 9532.028242111206 | 1069 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 224 | 0 | 198 | 0.0 | 0.0 | None | None | 26 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `35`
- Gating Δ: `11015`
- No-generation Δ: `224606`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 4.0957, "current_avg_pnl": 3.4855, "current_win_rate": 100.0, "previous_avg_pnl": -0.6102, "previous_win_rate": 33.3, "win_rate_delta": 66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.9171, "current_avg_pnl": -1.3128, "current_win_rate": 0.0, "previous_avg_pnl": -3.2299, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 1069, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 5583.42, "median_terminal_delta_sec": 5582.66, "sl_rate_delta": -100.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 26, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
