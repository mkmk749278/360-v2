# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `4146` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 2206 | 2206 | 1692 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 13409 | 13409 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 10902 | 10902 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 10872 | 10269 | 633 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 10903 | 10599 | 314 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 11282 | 11281 | 3 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 10051 | 10052 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 10913 | 10913 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 10915 | 10692 | 254 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 14042 | 14741 | 103 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 13409 | 11286 | 2750 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 11172 | 11172 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 10902 | 10903 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 10872 | 10872 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::RANGE_FADE | 10946 | 10694 | 316 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 10760 | 10341 | 528 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 9624 | 9015 | 635 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 9651 | 9573 | 84 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 13408 | 13409 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 10052 | 10054 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1054 | 1054 | 911 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 6 | 6 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 3108 | 3108 | 3041 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 567 | 567 | 565 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 243 | 243 | 225 | 4 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 6451 | 6451 | 3394 | 84 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 763 | 763 | 763 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 2102 | 2102 | 110 | 15 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 291 | 291 | 230 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=13409): breakout_not_found=6411, basic_filters_failed=4057, move_not_fresh=1965, breakout_stale=570, retest_proximity_failed=355, volume_spike_missing=49, rsi_reject=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=10902): cls_disabled_merged_into_lsr=10902
- **EVAL::DIVERGENCE_CONTINUATION** (total=10269): cvd_divergence_failed=3766, basic_filters_failed=3459, h1_trend_not_aligned=1831, ema_alignment_reject=960, retest_proximity_failed=205, missing_fvg_or_orderblock=48
- **EVAL::FAILED_AUCTION_RECLAIM** (total=10599): auction_not_detected=3889, basic_filters_failed=3263, reclaim_hold_failed=1687, tail_too_small=1297, regime_blocked=463
- **EVAL::FUNDING_EXTREME** (total=11281): funding_not_extreme=7288, basic_filters_failed=3526, rsi_reject=217, missing_funding_rate=164, ema_alignment_reject=77, momentum_reject=9
- **EVAL::LIQUIDATION_REVERSAL** (total=10052): cascade_threshold_not_met=6414, basic_filters_failed=3559, cvd_divergence_failed=39, rsi_reject=32, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=10913): no_ma_cross=7132, basic_filters_failed=3459, ma_cross_htf_misaligned=203, ma_cross_cooldown=119
- **EVAL::MEAN_REVERT** (total=10692): no_extension=8424, basic_filters_failed=2268
- **EVAL::MOVER_AVWAP_SCALP** (total=14741): no_avwap_tag=8343, basic_filters_failed=4064, no_mover_leg=1542, avwap_slope_against=463, no_avwap_reclaim=139, avwap_reclaim_no_volume=131, anchor_too_recent=59
- **EVAL::MOVER_TREND_PULLBACK** (total=11286): basic_filters_failed=4063, no_reclaim=3984, mover_run_too_small=2329, no_pullback_tag=910
- **EVAL::OPENING_RANGE_BREAKOUT** (total=11172): feature_disabled=11172
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=10903): regime_blocked=6712, breakout_not_found=3023, basic_filters_failed=919, adx_reject=241, ema_alignment_reject=8
- **EVAL::QUIET_COMPRESSION_BREAK** (total=10872): regime_blocked=4640, compression_not_detected=3762, basic_filters_failed=2344, breakout_not_detected=124, volume_confirmation_failed=2
- **EVAL::RANGE_FADE** (total=10694): no_range_edge=8426, basic_filters_failed=2268
- **EVAL::SR_FLIP_RETEST** (total=10341): basic_filters_failed=3262, flip_close_not_confirmed=2049, long_break_volume_thin=1861, reclaim_hold_failed=968, whipsaw_flip=719, retest_out_of_zone=670, regime_blocked=463, long_disabled=198, wick_quality_failed=114, ema_alignment_reject=29, missing_fvg_or_orderblock=6, long_acceptance_not_held=2
- **EVAL::STANDARD** (total=9015): momentum_reject=3201, basic_filters_failed=1922, adx_reject=1744, sweeps_not_detected=967, macd_reject=595, ema_alignment_reject=566, rsi_reject=16, invalid_sl_geometry=4
- **EVAL::TREND_PULLBACK** (total=9573): h1_trend_not_aligned=3248, h1_pullback_not_confirmed=1524, ema_alignment_reject=1436, basic_filters_failed=1316, no_ema_reclaim_close=980, ema_not_tested_prev=608, body_conviction_fail=256, rsi_reject=105, no_prev_low_break=39, momentum_flat=21, prev_already_below_emas=15, missing_fvg_or_orderblock=11, prev_already_above_emas=10, ema21_not_tagged=2, no_prev_high_break=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=13409): breakout_not_found=7605, basic_filters_failed=4057, move_not_fresh=1226, breakout_stale=291, retest_proximity_failed=216, volume_spike_missing=11, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=10054): momentum_reject=6509, recent_ticks_insufficient=2787, basic_filters_failed=758

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=82): setup_compat:regime_VOLATILE_UNSUITABLE=78, setup_compat:regime_BREAKOUT_EXPANSION=4
- **FAILED_AUCTION_RECLAIM** (total=329): setup_compat:regime_STRONG_TREND=158, execution:overextended=100, context_floor=71
- **LIQUIDITY_SWEEP_REVERSAL** (total=650): execution:trigger_not_confirmed=252, execution:overextended=205, setup_compat:regime_STRONG_TREND=193
- **MA_CROSS_TREND_SHIFT** (total=2): setup_compat:regime_CLEAN_RANGE=1, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=401): setup_compat:regime_WEAK_TREND=167, execution:overextended=134, setup_compat:regime_STRONG_TREND=100
- **MOVER_AVWAP_SCALP** (total=225): execution:overextended=197, execution:trigger_not_confirmed=28
- **MOVER_TREND_PULLBACK** (total=3071): execution:overextended=2054, execution:trigger_not_confirmed=1017
- **RANGE_FADE** (total=511): setup_compat:regime_STRONG_TREND=272, execution:overextended=125, setup_compat:regime_WEAK_TREND=113, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **TREND_PULLBACK_EMA** (total=207): setup_compat:regime_CLEAN_RANGE=160, setup_compat:regime_DIRTY_RANGE=32, context_floor=15

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 20948 | 31.7% |
| RANGING | 16432 | 24.8% |
| QUIET | 14523 | 22.0% |
| TRENDING_UP | 10158 | 15.4% |
| VOLATILE | 4096 | 6.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **54**
- Average confidence gap to threshold: **7.07** (samples=54) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ENAUSDT=15, XMRUSDT=11, DOTUSDT=6, SOLUSDT=6, ETHUSDT=5, WLFIUSDT=4, NEARUSDT=3, PENGUUSDT=3, XLMUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 66 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 17 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 153 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 39 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 14 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 10 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 20 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 15 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1829 |
| SR_FLIP_RETEST | filtered | min_confidence | 190 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 8 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 323 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 24 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 83 | 59.50 | 65.00 | 5.50 | 19.49 | 19.97 | 18.32 | 2.37 | 4.12 |
| DIVERGENCE_CONTINUATION | kept | 153 | 72.01 | 65.00 | -7.01 | 21.32 | 19.91 | 17.11 | 2.45 | 2.39 |
| FAILED_AUCTION_RECLAIM | filtered | 43 | 47.23 | 65.00 | 17.77 | 20.24 | 18.52 | 20.00 | 2.99 | 10.86 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 5 | 56.90 | 65.00 | 8.10 | 20.42 | 20.00 | 17.00 | 3.00 | 14.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 74.50 | 65.00 | -9.50 | 19.27 | 19.27 | 17.00 | 2.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 10 | 74.31 | 65.00 | -9.31 | 19.47 | 17.43 | 15.80 | 3.50 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 35 | 56.85 | 64.86 | 8.01 | 21.26 | 19.38 | 15.80 | 4.64 | 13.11 |
| MOVER_TREND_PULLBACK | kept | 1829 | 76.99 | 65.00 | -11.99 | 20.48 | 18.57 | 15.80 | 4.42 | 0.10 |
| SR_FLIP_RETEST | filtered | 198 | 59.12 | 64.13 | 5.01 | 21.01 | 19.87 | 15.59 | 1.39 | 8.37 |
| SR_FLIP_RETEST | kept | 323 | 68.39 | 65.00 | -3.39 | 21.07 | 19.87 | 17.14 | 1.82 | 0.63 |
| TREND_PULLBACK_EMA | kept | 24 | 74.12 | 65.00 | -9.12 | 20.22 | 20.00 | 17.25 | 4.12 | -2.75 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 83 | 59.50 | 23.07 | 15.47 | 4.16 | 10.43 | 5.01 | 7.99 | 2.37 |
| DIVERGENCE_CONTINUATION | kept | 153 | 72.01 | 23.59 | 16.17 | 6.43 | 12.24 | 5.33 | 9.12 | 2.45 |
| FAILED_AUCTION_RECLAIM | filtered | 43 | 47.23 | 22.02 | 17.63 | 5.58 | 14.49 | 5.00 | 5.37 | 2.99 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 5 | 56.90 | 25.00 | 14.00 | 6.00 | 9.00 | 5.00 | 9.30 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 74.50 | 17.00 | 14.00 | 9.00 | 14.00 | 8.50 | 10.00 | 2.00 |
| MOVER_AVWAP_SCALP | kept | 10 | 74.31 | 17.40 | 18.00 | 10.35 | 14.00 | 5.50 | 5.56 | 3.50 |
| MOVER_TREND_PULLBACK | filtered | 35 | 56.85 | 18.54 | 18.00 | 8.74 | 12.34 | 5.03 | 7.81 | 4.64 |
| MOVER_TREND_PULLBACK | kept | 1829 | 76.99 | 19.77 | 18.04 | 7.81 | 12.46 | 5.37 | 9.27 | 4.42 |
| SR_FLIP_RETEST | filtered | 198 | 59.12 | 18.49 | 17.60 | 3.50 | 12.24 | 5.81 | 8.46 | 1.39 |
| SR_FLIP_RETEST | kept | 323 | 68.39 | 20.63 | 17.88 | 3.37 | 12.56 | 5.12 | 8.65 | 1.82 |
| TREND_PULLBACK_EMA | kept | 24 | 74.12 | 17.33 | 18.00 | 7.50 | 14.00 | 5.00 | 8.17 | 4.12 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 83 | 59.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.58 | 0.00 | 0.00 | 0.00 | **0.58** |
| DIVERGENCE_CONTINUATION | kept | 153 | 72.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.94 | 0.12 | 0.00 | 0.00 | **1.06** |
| FAILED_AUCTION_RECLAIM | filtered | 43 | 47.23 | 0.00 | 0.00 | 0.00 | 0.00 | 2.57 | 0.00 | 0.00 | 0.00 | **2.57** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 5 | 56.90 | 0.00 | 0.00 | 14.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **14.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 74.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 10 | 74.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 35 | 56.85 | 0.00 | 0.00 | 0.00 | 0.00 | 10.49 | 2.00 | 0.00 | 0.31 | **12.80** |
| MOVER_TREND_PULLBACK | kept | 1829 | 76.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.06 | 0.00 | 0.00 | **0.10** |
| SR_FLIP_RETEST | filtered | 198 | 59.12 | 0.00 | 0.00 | 0.12 | 0.00 | 0.33 | 0.15 | 0.00 | 0.00 | **0.60** |
| SR_FLIP_RETEST | kept | 323 | 68.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | **0.06** |
| TREND_PULLBACK_EMA | kept | 24 | 74.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1179 (25.6%) | WOULD_LOSE=974 | WOULD_EXPIRE=2447 | pending (awaiting window)=398

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:FAILED_AUCTION_RECLAIM | 402 | 0.0% | 155.9 | 0.0 | +0.39 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 16 | 0.0% | 1.1 | 0.0 | +0.07 | **INSUFFICIENT_SAMPLE** |
| context_floor:TREND_PULLBACK_EMA | 11 | 0.0% | 2.8 | 0.0 | +0.25 | **INSUFFICIENT_SAMPLE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 15 | 0.0% | 1.1 | 0.0 | +0.08 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 86 | 40.7% | 10.5 | 19.2 | -0.10 | **TUNE** |
| dispatch_staleness_v2 | 638 | 64.1% | 104.2 | 199.1 | -0.15 | **TUNE** |
| level_still_in_play | 1478 | 15.9% | 220.0 | 128.5 | +0.06 | **TUNE** |
| min_confidence | 1369 | 28.0% | 607.0 | 431.7 | +0.13 | **KEEP** |
| quiet_scalp_block | 251 | 12.4% | 96.7 | 31.4 | +0.26 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 10 | 30.0% | 4.2 | 1.9 | +0.23 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 46 | 58.7% | 19.5 | 19.7 | -0.00 | **TUNE** |
| shadow_unit:SHADOW_MEAN_REVERT | 154 | 17.5% | 122.6 | 73.5 | +0.32 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 124 | 22.6% | 84.0 | 85.9 | -0.02 | **TUNE** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 75826 across 20 strategies; 1722 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 17280 | 53/17227/0 | 62% | +0.18 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.27R) |
| FAILED_AUCTION_RECLAIM | 13353 | 26/13327/0 | 50% | -0.03 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 12635 | 2/12633/0 | 44% | -0.21 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.15R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.30R) |
| DIVERGENCE_CONTINUATION | 7073 | 10/7063/0 | 50% | -0.03 | NY/MARKUP/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.34R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| QUIET_COMPRESSION_BREAK | 5244 | 2/5242/0 | 47% | -0.02 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 3054 | 0/0/3054 | 39% | -0.02 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.06R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| MEAN_REVERT | 2999 | 0/2999/0 | 80% | +0.59 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| LIQUIDITY_SWEEP_REVERSAL | 2933 | 9/2924/0 | 41% | -0.16 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| SHADOW_RANGE_FADE | 2861 | 0/0/2861 | 41% | +0.26 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.09R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_FUNDING_FADE | 2212 | 0/0/2212 | 44% | -0.24 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.42R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| RANGE_FADE | 1901 | 0/1901/0 | 3% | -0.99 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.22R) |
| VOLUME_SURGE_BREAKOUT | 1315 | 12/1303/0 | 42% | +0.01 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 1195 | 2/1193/0 | 49% | -0.17 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 384 | 2/382/0 | 33% | -0.19 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| MOVER_AVWAP_SCALP | 311 | 22/289/0 | 42% | -0.20 | NY/MARKUP/CASCADE/BTC_FALLING (+0.55R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 232 | 0/0/232 | 46% | -0.10 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.00R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 4 | 1/3/0 | 75% | +0.16 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 35 | 40% / +0.06R | 35 | 34% / -0.16R | -0.22 | **FIXED** |
| TREND_PULLBACK_EMA | 28 | 50% / -0.16R | 28 | 54% / +0.05R | +0.21 | **ATR** |
| MEAN_REVERT | 238 | 58% / +0.14R | 238 | 55% / +0.27R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| MOVER_AVWAP_SCALP | 62 | 45% / -0.05R | 62 | 53% / +0.04R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 1782 | 47% / -0.13R | 1782 | 50% / -0.05R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 347 | 47% / -0.16R | 347 | 51% / -0.07R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1609 | 46% / -0.10R | 1609 | 46% / -0.07R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 751 | 45% / -0.05R | 751 | 45% / -0.07R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 352 | 50% / -0.02R | 352 | 55% / -0.01R | +0.02 | **ATR** |
| RANGE_FADE | 139 | 2% / -1.05R | 139 | 2% / -1.04R | +0.01 | **ATR** |
| MOVER_TREND_PULLBACK | 1735 | 57% / +0.05R | 1735 | 60% / +0.05R | +0.01 | **ATR** |
| BREAKDOWN_SHORT | 10 | 20% / -0.31R | 10 | 20% / -0.31R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 7 | 14% / -0.71R | 7 | 43% / -0.21R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 4 | 75% / +0.10R | 4 | 75% / -0.13R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 83% / +0.45R | 6 | 83% / +0.12R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 765 | 30% | -0.13R | 118 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 52 | 52% | +0.02R | 34 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 3 | 0% | -0.14R | 3 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 363 | 25% / -5.16R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 2 | 0% / -2.41R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 348 | 34% / -1.66R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 351 | 37% / -1.17R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 10 | 20% / -5.55R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 110 | 11% / -9.21R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 112 | 53% / +0.80R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 65 | 31% / -4.80R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 9 | 11% / -9.42R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 15 | 13% / -5.37R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 6 | 33% / -0.25R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 1 | 0% / -1.85R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| MOVER_AVWAP_SCALP | dispatch_cooldown | 10 | 100.0% | -1.02 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 47 | 87.2% | -0.30 | **DROP** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 574 | 64.1% | -0.14 | **TUNE** |
| SR_FLIP_RETEST | level_still_in_play | 142 | 23.2% | -0.02 | **TUNE** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 124 | 22.6% | -0.02 | **TUNE** |
| MOVER_TREND_PULLBACK | dispatch_cooldown | 61 | 41.0% | -0.01 | **TUNE** |
| SHADOW_FUNDING_FADE | shadow_unit:SHADOW_FUNDING_FADE | 46 | 58.7% | -0.00 | **TUNE** |
| FAILED_AUCTION_RECLAIM | level_still_in_play | 5 | 0.0% | +0.05 | **INSUFFICIENT_SAMPLE** |
| MOVER_AVWAP_SCALP | min_confidence | 3 | 0.0% | +0.05 | **INSUFFICIENT_SAMPLE** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 27 | 0.0% | +0.06 | **TUNE** |
| MOVER_TREND_PULLBACK | level_still_in_play | 1279 | 15.8% | +0.07 | **TUNE** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 16 | 0.0% | +0.07 | **INSUFFICIENT_SAMPLE** |
| MOVER_AVWAP_SCALP | dispatch_staleness_v2 | 3 | 0.0% | +0.07 | **INSUFFICIENT_SAMPLE** |
| VOLUME_SURGE_BREAKOUT | context_floor:VOLUME_SURGE_BREAKOUT | 15 | 0.0% | +0.08 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | min_confidence | 611 | 32.1% | +0.08 | **TUNE** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 25 | 0.0% | +0.09 | **TUNE** |
| SR_FLIP_RETEST | dispatch_cooldown | 15 | 0.0% | +0.13 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | min_confidence | 104 | 0.0% | +0.13 | **KEEP** |
| MOVER_TREND_PULLBACK | min_confidence | 562 | 31.7% | +0.14 | **KEEP** |
| LIQUIDITY_SWEEP_REVERSAL | dispatch_staleness_v2 | 14 | 0.0% | +0.17 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | quiet_scalp_block | 14 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | quiet_scalp_block | 7 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | quiet_scalp_block | 140 | 13.6% | +0.19 | **KEEP** |
| SR_FLIP_RETEST | quiet_scalp_block | 37 | 32.4% | +0.20 | **KEEP** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 10 | 30.0% | +0.23 | **INSUFFICIENT_SAMPLE** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 22 · alerting: **3** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 26/360 disagreed (7.2%) (streak 19/6) (sustained 19 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.46R (bound 0.3) (streak 19/6) (sustained 19 cycles)
- **ALERT** `mean_revert_emission` — 547 detections since last emission (emitted_total=0) — and the blocked candidates measure +0.59R over n=2999, so the gating is COSTING us. Check gate rejections. (streak 19/6) (sustained 19 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=0 fanouts=4 (gaps: skip 4, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 63306.00 | 0 |
| candle_coverage | ok | 104/104 symbols with ≥20 15m candles, 104/104 updated within 45m | 0 |
| context_emission_policy | ok | output +23 / upstream +31 | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.46R (bound 0.3) (streak 19/6) | 19 |
| emission_controller | ok | last cycle 0s ago; live_overrides=18 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=9 wasted_promotions=0 pruned=0 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +13 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 547 detections since last emission (emitted_total=0) — and the blocked candidates measure +0.59R over n=2999, so the gating is COSTING us. Check gate rejections. (streak 19/6) | 19 |
| mean_revert_path | ok | output +0 / upstream +13 | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.99R over n=1901 — emitting them would lose money | 0 |
| range_fade_path | ok | output +12 / upstream +13 | 0 |
| sar_alignment_crosscheck | violating | 26/360 disagreed (7.2%) (streak 19/6) | 19 |
| sar_exit_shadow | ok | output +6 / upstream +13 | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +77 / upstream +13 | 0 |
| suppression_audit | ok | output +13 / upstream +31 | 0 |
| tuned_variants | ok | seen=938 stamped=117 skipped=820 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `25494`
- `Path funnel` emissions: `7`
- `Regime distribution` emissions: `7`
- `QUIET_SCALP_BLOCK` events: `54`
- `confidence_gate` events: `2717`
- `free_channel_post` events: `1`
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
| futures_liq | 1 | 1888 | 1888 | 1888 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **1**

| Source | Count |
|---|---:|
| signal_close | 1 |

- By severity: HIGH=1

## Dependency readiness
- cvd: presence[present=47115] state[populated=47115] buckets[many=47115] sources[none] quality[none]
- funding_rate: presence[absent=7858, present=39257] state[empty=7858, populated=39257] buckets[few=39257, none=7858] sources[none] quality[none]
- liquidation_clusters: presence[absent=29792, present=17323] state[empty=29792, populated=17323] buckets[few=13196, none=29792, some=4127] sources[none] quality[none]
- oi_snapshot: presence[absent=7407, present=39708] state[empty=7407, populated=39708] buckets[many=39708, none=7407] sources[none] quality[none]
- order_book: presence[absent=14589, present=32526] state[populated=32526, unavailable=14589] buckets[few=32526, none=14589] sources[book_ticker=32526, unavailable=14589] quality[none=14589, top_of_book_only=32526]
- orderblocks: presence[absent=47115] state[empty=47115] buckets[none=47115] sources[not_implemented=47115] quality[none]
- recent_ticks: presence[present=47115] state[populated=47115] buckets[many=47115] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.4143985509872437` sec
- Median create→first breach: `6130.479948997498` sec
- Median create→terminal: `6132.115005970001` sec
- Median first breach→terminal: `3.4000844955444336` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.7317 | 374.401328086853 | 376.5757050514221 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 3.9316 | 1125.9252099990845 | 1133.9187018871307 |
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 80.0 | 0.0 | 0.0 | -1.6072 | 6844.409582853317 | 6845.827055931091 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.876 | 6806.162504911423 | 6808.958214998245 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 2102 | 15 | 110 | 0.0 | 0.0 | None | None | 1992 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 291 | 0 | 230 | 0.0 | 0.0 | None | None | 61 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-158`
- Gating Δ: `-158519`
- No-generation Δ: `-2297035`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -4.1909, "current_avg_pnl": -1.6072, "current_win_rate": 0.0, "previous_avg_pnl": 2.5837, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -71, "geometry_changed_delta": 0, "geometry_preserved_delta": -6543, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3637.19, "median_terminal_delta_sec": -3643.12, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -183, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2004.34, "median_terminal_delta_sec": -2005.91, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
