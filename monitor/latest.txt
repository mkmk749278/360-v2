# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::VOLUME_SURGE_BREAKOUT, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::VOLUME_SURGE_BREAKOUT**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `12951` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1909 | 1909 | 1759 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 9636 | 9635 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 9140 | 9140 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 9105 | 8677 | 462 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 9143 | 8763 | 414 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 9154 | 9142 | 16 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 8115 | 8112 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 9177 | 9184 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 9184 | 8586 | 743 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 9939 | 10471 | 22 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 9640 | 8436 | 1501 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 8868 | 8870 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 9140 | 9143 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 9095 | 9092 | 13 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 9329 | 8430 | 1018 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 8806 | 8534 | 555 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 8015 | 7820 | 227 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 8047 | 8050 | 1 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 9635 | 9636 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 8116 | 8112 | 14 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1653 | 1653 | 863 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 64 | 64 | 64 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 19 | 19 | 19 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 2356 | 2356 | 2356 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 1826 | 1826 | 1176 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 45 | 45 | 44 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 2855 | 2855 | 2042 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 168 | 168 | 130 | 0 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1556 | 1556 | 1483 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 3015 | 3015 | 2655 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 47 | 47 | 47 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 599 | 599 | 599 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=9635): breakout_not_found=4961, basic_filters_failed=2620, move_not_fresh=1708, breakout_stale=230, retest_proximity_failed=98, move_exhausted=16, ema_alignment_reject=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=9140): cls_disabled_merged_into_lsr=9140
- **EVAL::DIVERGENCE_CONTINUATION** (total=8677): cvd_divergence_failed=3933, basic_filters_failed=2019, h1_trend_not_aligned=1659, ema_alignment_reject=936, retest_proximity_failed=85, missing_fvg_or_orderblock=21, cvd_insufficient=14, regime_blocked=10
- **EVAL::FAILED_AUCTION_RECLAIM** (total=8763): auction_not_detected=3081, reclaim_hold_failed=2346, basic_filters_failed=2017, tail_too_small=1201, regime_blocked=118
- **EVAL::FUNDING_EXTREME** (total=9142): funding_not_extreme=6526, basic_filters_failed=1988, ema_alignment_reject=250, missing_funding_rate=201, momentum_reject=136, cvd_divergence_failed=25, rsi_reject=12, missing_fvg_or_orderblock=4
- **EVAL::LIQUIDATION_REVERSAL** (total=8112): cascade_threshold_not_met=6056, basic_filters_failed=2004, cvd_divergence_failed=27, rsi_reject=23, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=9184): no_ma_cross=7011, basic_filters_failed=2020, ma_cross_cooldown=90, ma_cross_htf_misaligned=63
- **EVAL::MEAN_REVERT** (total=8586): no_extension=7675, basic_filters_failed=911
- **EVAL::MOVER_AVWAP_SCALP** (total=10471): no_avwap_tag=3137, no_mover_leg=2833, basic_filters_failed=2633, no_avwap_reclaim=985, avwap_slope_against=657, avwap_reclaim_no_volume=226
- **EVAL::MOVER_TREND_PULLBACK** (total=8436): mover_run_too_small=3380, basic_filters_failed=2626, no_reclaim=2263, no_pullback_tag=167
- **EVAL::OPENING_RANGE_BREAKOUT** (total=8870): feature_disabled=8870
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=9143): regime_blocked=4909, breakout_not_found=2852, basic_filters_failed=1184, adx_reject=198
- **EVAL::QUIET_COMPRESSION_BREAK** (total=9092): regime_blocked=4336, compression_not_detected=3124, basic_filters_failed=833, breakout_not_detected=483, volume_confirmation_failed=195, macd_reject=84, rsi_reject=37
- **EVAL::RANGE_FADE** (total=8430): no_range_edge=7519, basic_filters_failed=911
- **EVAL::SR_FLIP_RETEST** (total=8534): basic_filters_failed=2016, whipsaw_flip=1360, long_break_volume_thin=1194, flip_close_not_confirmed=1116, retest_out_of_zone=1009, reclaim_hold_failed=718, long_disabled=546, wick_quality_failed=164, ema_alignment_reject=149, regime_blocked=118, long_acceptance_not_held=106, missing_fvg_or_orderblock=38
- **EVAL::STANDARD** (total=7820): momentum_reject=3240, adx_reject=2113, basic_filters_failed=810, sweeps_not_detected=622, ema_alignment_reject=542, macd_reject=362, rsi_reject=109, invalid_sl_geometry=22
- **EVAL::TREND_PULLBACK** (total=8050): ema_alignment_reject=1820, h1_trend_not_aligned=1732, basic_filters_failed=1468, ema_not_tested_prev=988, no_ema_reclaim_close=723, h1_pullback_not_confirmed=533, body_conviction_fail=377, rsi_reject=309, prev_already_above_emas=75, regime_blocked=10, no_prev_high_break=7, momentum_flat=5, prev_already_below_emas=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=9636): breakout_not_found=5609, basic_filters_failed=2620, move_not_fresh=953, breakout_stale=344, retest_proximity_failed=88, volume_spike_missing=20, missing_fvg_or_orderblock=2
- **EVAL::WHALE_MOMENTUM** (total=8112): momentum_reject=6063, recent_ticks_insufficient=1637, basic_filters_failed=412

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=96): context_floor=90, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **FAILED_AUCTION_RECLAIM** (total=630): setup_compat:regime_STRONG_TREND=273, context_floor=219, execution:overextended=138
- **FUNDING_EXTREME_SIGNAL** (total=64): execution:trigger_not_confirmed=64
- **LIQUIDATION_REVERSAL** (total=19): execution:trigger_not_confirmed=19
- **LIQUIDITY_SWEEP_REVERSAL** (total=1018): setup_compat:regime_STRONG_TREND=446, execution:trigger_not_confirmed=430, execution:overextended=142
- **MEAN_REVERT** (total=861): execution:overextended=542, setup_compat:regime_WEAK_TREND=319
- **MOVER_AVWAP_SCALP** (total=44): execution:trigger_not_confirmed=38, execution:overextended=6
- **MOVER_TREND_PULLBACK** (total=1785): execution:trigger_not_confirmed=1129, execution:overextended=656
- **QUIET_COMPRESSION_BREAK** (total=38): context_floor=38
- **RANGE_FADE** (total=362): setup_compat:regime_STRONG_TREND=236, setup_compat:regime_VOLATILE_UNSUITABLE=82, setup_compat:regime_WEAK_TREND=44
- **TREND_PULLBACK_EMA** (total=47): setup_compat:regime_CLEAN_RANGE=39, setup_compat:regime_DIRTY_RANGE=8
- **WHALE_MOMENTUM** (total=599): execution:trigger_not_confirmed=599

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 16761 | 33.8% |
| RANGING | 14718 | 29.7% |
| QUIET | 9681 | 19.5% |
| TRENDING_UP | 6528 | 13.2% |
| VOLATILE | 1865 | 3.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **22**
- Average confidence gap to threshold: **13.55** (samples=22) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ZECUSDT=11, SUIUSDT=7, XLMUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 2 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 48 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 22 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 106 |
| MEAN_REVERT | filtered | min_confidence | 82 |
| MEAN_REVERT | kept | min_confidence_pass | 274 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 41 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 730 |
| SR_FLIP_RETEST | filtered | min_confidence | 39 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 48 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 58.50 | 60.00 | 1.50 | 20.30 | 18.60 | 20.00 | 5.00 | 6.80 |
| DIVERGENCE_CONTINUATION | kept | 2 | 67.15 | 65.00 | -2.15 | 20.50 | 19.40 | 20.00 | 0.00 | 3.40 |
| FAILED_AUCTION_RECLAIM | filtered | 70 | 50.29 | 63.06 | 12.77 | 20.13 | 19.99 | 20.00 | 3.75 | 6.88 |
| FAILED_AUCTION_RECLAIM | kept | 106 | 71.24 | 65.00 | -6.24 | 20.11 | 19.65 | 20.00 | 4.72 | 0.41 |
| MEAN_REVERT | filtered | 82 | 61.65 | 65.00 | 3.35 | 22.48 | 14.00 | 19.20 | 0.00 | 12.00 |
| MEAN_REVERT | kept | 274 | 68.03 | 65.00 | -3.03 | 22.03 | 14.30 | 18.99 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 74.50 | 65.00 | -9.50 | 16.60 | 18.40 | 15.80 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 41 | 64.70 | 65.00 | 0.30 | 22.28 | 19.60 | 15.80 | 4.00 | 12.00 |
| MOVER_TREND_PULLBACK | kept | 730 | 71.44 | 65.00 | -6.44 | 21.86 | 19.23 | 15.80 | 4.64 | 0.67 |
| SR_FLIP_RETEST | filtered | 39 | 60.13 | 65.00 | 4.87 | 19.99 | 20.00 | 15.20 | 1.46 | 6.65 |
| SR_FLIP_RETEST | kept | 48 | 70.38 | 65.00 | -5.38 | 20.21 | 20.00 | 15.20 | 2.47 | -2.44 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 58.50 | 25.00 | 8.00 | 3.00 | 10.00 | 5.00 | 9.30 | 5.00 |
| DIVERGENCE_CONTINUATION | kept | 2 | 67.15 | 25.00 | 13.00 | 3.00 | 14.00 | 6.75 | 8.80 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 70 | 50.29 | 20.03 | 14.80 | 5.66 | 12.31 | 6.80 | 4.30 | 3.75 |
| FAILED_AUCTION_RECLAIM | kept | 106 | 71.24 | 22.89 | 14.04 | 6.93 | 9.23 | 7.11 | 6.87 | 4.72 |
| MEAN_REVERT | filtered | 82 | 61.65 | 17.00 | 18.00 | 13.50 | 12.00 | 8.50 | 4.65 | 0.00 |
| MEAN_REVERT | kept | 274 | 68.03 | 20.36 | 18.00 | 6.46 | 12.14 | 6.31 | 4.76 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 74.50 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 3.00 |
| MOVER_TREND_PULLBACK | filtered | 41 | 64.70 | 17.00 | 18.00 | 15.00 | 10.00 | 8.00 | 4.70 | 4.00 |
| MOVER_TREND_PULLBACK | kept | 730 | 71.44 | 18.89 | 18.00 | 8.47 | 10.51 | 5.25 | 6.35 | 4.64 |
| SR_FLIP_RETEST | filtered | 39 | 60.13 | 16.79 | 18.00 | 8.69 | 14.00 | 5.00 | 2.83 | 1.46 |
| SR_FLIP_RETEST | kept | 48 | 70.38 | 24.83 | 18.00 | 3.12 | 11.50 | 8.25 | 2.20 | 2.47 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 58.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 2 | 67.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 70 | 50.29 | 0.00 | 0.00 | 0.00 | 0.00 | 2.16 | 0.00 | 0.00 | 0.00 | **2.16** |
| FAILED_AUCTION_RECLAIM | kept | 106 | 71.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | **0.41** |
| MEAN_REVERT | filtered | 82 | 61.65 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 274 | 68.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 1 | 74.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 41 | 64.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_TREND_PULLBACK | kept | 730 | 71.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | **0.67** |
| SR_FLIP_RETEST | filtered | 39 | 60.13 | 0.00 | 0.00 | 0.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.49** |
| SR_FLIP_RETEST | kept | 48 | 70.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1191 (32.8%) | WOULD_LOSE=586 | WOULD_EXPIRE=1852 | pending (awaiting window)=1371

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 41 | 0.0% | 48.5 | 0.0 | +1.18 | **KEEP** |
| context_floor:DIVERGENCE_CONTINUATION | 238 | 21.4% | 198.3 | 69.8 | +0.54 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 254 | 1.6% | 51.8 | 7.4 | +0.17 | **KEEP** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 10 | 0.0% | 17.9 | 0.0 | +1.79 | **INSUFFICIENT_SAMPLE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 9 | 0.0% | 10.1 | 0.0 | +1.13 | **INSUFFICIENT_SAMPLE** |
| data_stale | 69 | 0.0% | 30.3 | 0.0 | +0.44 | **KEEP** |
| dispatch_staleness | 1225 | 49.7% | 82.3 | 318.3 | -0.19 | **TUNE** |
| level_still_in_play | 989 | 40.7% | 92.3 | 148.3 | -0.06 | **TUNE** |
| min_confidence | 564 | 13.7% | 269.5 | 101.2 | +0.30 | **KEEP** |
| quiet_scalp_block | 109 | 3.7% | 36.4 | 3.8 | +0.30 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 8 | 25.0% | 1.2 | 1.4 | -0.02 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 6 | 50.0% | 3.1 | 2.2 | +0.15 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 66 | 36.4% | 45.5 | 32.1 | +0.20 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 41 | 34.1% | 26.2 | 44.0 | -0.44 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 54631 across 20 strategies; 1250 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 14087 | 38/14049/0 | 61% | +0.19 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.13R) |
| FAILED_AUCTION_RECLAIM | 10018 | 20/9998/0 | 51% | +0.04 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 8480 | 2/8478/0 | 42% | -0.12 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.14R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.20R) |
| DIVERGENCE_CONTINUATION | 4847 | 5/4842/0 | 45% | -0.02 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| QUIET_COMPRESSION_BREAK | 3895 | 0/3895/0 | 45% | +0.01 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 2524 | 0/0/2524 | 34% | -0.14 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.61R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_RANGE_FADE | 2212 | 0/0/2212 | 35% | +0.15 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.61R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| MEAN_REVERT | 2153 | 0/2153/0 | 77% | +0.52 | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (+1.27R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-1.05R) |
| LIQUIDITY_SWEEP_REVERSAL | 1765 | 3/1762/0 | 37% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.17R) |
| SHADOW_FUNDING_FADE | 1373 | 0/0/1373 | 34% | -0.40 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 943 | 8/935/0 | 39% | -0.10 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| RANGE_FADE | 628 | 0/628/0 | 10% | -0.49 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.21R) |
| TREND_PULLBACK_EMA | 593 | 0/593/0 | 42% | -0.16 | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.36R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| WHALE_MOMENTUM | 242 | 0/242/0 | 55% | -0.04 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 239 | 5/234/0 | 54% | +0.31 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 236 | 0/236/0 | 42% | +0.12 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 211 | 10/201/0 | 19% | -0.63 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 176 | 0/0/176 | 46% | -0.11 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.16R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +1.95R (n=34, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.21R (n=31, NEGATIVE); `RANGE_FADE @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.21R (n=31, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.20R (n=38, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 25 | 44% / +0.02R | 25 | 32% / -0.22R | -0.24 | **FIXED** |
| TREND_PULLBACK_EMA | 21 | 52% / -0.12R | 21 | 57% / +0.07R | +0.19 | **ATR** |
| MOVER_AVWAP_SCALP | 40 | 42% / -0.08R | 40 | 55% / +0.09R | +0.17 | **ATR** |
| RANGE_FADE | 20 | 15% / -0.15R | 20 | 15% / -0.29R | -0.14 | **FIXED** |
| WHALE_MOMENTUM | 20 | 35% / -0.16R | 20 | 30% / -0.26R | -0.10 | **FIXED** |
| MEAN_REVERT | 111 | 58% / +0.11R | 111 | 53% / +0.21R | +0.10 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 192 | 44% / -0.13R | 192 | 52% / -0.06R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 1121 | 45% / -0.08R | 1121 | 49% / -0.02R | +0.05 | **ATR** |
| MOVER_TREND_PULLBACK | 1212 | 63% / +0.17R | 1212 | 66% / +0.13R | -0.04 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 1172 | 50% / +0.01R | 1172 | 49% / +0.02R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 559 | 45% / -0.01R | 559 | 45% / -0.02R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 260 | 48% / -0.02R | 260 | 53% / -0.01R | +0.00 | **ATR** |
| BREAKDOWN_SHORT | 8 | 25% / -0.27R | 8 | 25% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 3 | 0% / -1.05R | 3 | 67% / -0.00R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0% / +0.00R | 1 | 0% / +0.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 16 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=-0.37R (bound 0.3) (streak 10/6) (sustained 10 cycles)
- **ALERT** `mean_revert_emission` — 1861 detections since last emission (emitted_total=0) — check gate rejections (streak 10/6) (sustained 10 cycles)
- **ALERT** `range_fade_emission` — 1589 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 10/6) (sustained 10 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 65614.70 | 0 |
| candle_coverage | ok | 87/89 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +91 / upstream +41 | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=-0.37R (bound 0.3) (streak 10/6) | 10 |
| emission_controller | ok | last cycle 928s ago; live_overrides=11 | 0 |
| geometry_ab | ok | output +6 / upstream +69 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1861 detections since last emission (emitted_total=0) — check gate rejections (streak 10/6) | 10 |
| mean_revert_path | ok | output +129 / upstream +69 | 0 |
| range_fade_emission | violating | 1589 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 10/6) | 10 |
| range_fade_path | ok | output +110 / upstream +69 | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| strategy_edge | ok | output +234 / upstream +69 | 0 |
| suppression_audit | ok | output +69 / upstream +41 | 0 |
| tuned_variants | ok | seen=1 stamped=1 skipped=0 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `18515`
- `Path funnel` emissions: `6`
- `Regime distribution` emissions: `6`
- `QUIET_SCALP_BLOCK` events: `22`
- `confidence_gate` events: `1398`
- `free_channel_post` events: `0`
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
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=39073] state[populated=39073] buckets[few=36, many=38805, some=232] sources[none] quality[none]
- funding_rate: presence[absent=3605, present=35468] state[empty=3605, populated=35468] buckets[few=35468, none=3605] sources[none] quality[none]
- liquidation_clusters: presence[absent=23656, present=15417] state[empty=23656, populated=15417] buckets[few=12619, none=23656, some=2798] sources[none] quality[none]
- oi_snapshot: presence[absent=3036, present=36037] state[empty=3036, populated=36037] buckets[many=36037, none=3036] sources[none] quality[none]
- order_book: presence[absent=10395, present=28678] state[populated=28678, unavailable=10395] buckets[few=28678, none=10395] sources[book_ticker=28678, unavailable=10395] quality[none=10395, top_of_book_only=28678]
- orderblocks: presence[absent=39073] state[empty=39073] buckets[none=39073] sources[not_implemented=39073] quality[none]
- recent_ticks: presence[absent=599, present=38474] state[empty=599, populated=38474] buckets[many=38474, none=599] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.756477952003479` sec
- Median create→first breach: `1817.8173025846481` sec
- Median create→terminal: `1818.6579765081406` sec
- Median first breach→terminal: `0.8783080577850342` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 7.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 7.1}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2935 | 2399.5611044168472 | 2400.2125124931335 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 4.5223 | 3680.466847896576 | 3689.3439350128174 |
| MOVER_TREND_PULLBACK | 10 | 10 | 0.0 | 40.0 | 0.0 | 0.0 | -1.4673 | 1403.3229140043259 | 1404.6139899492264 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3698.725870847702 | 3700.213966846466 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 3015 | 2 | 2655 | 0.0 | 0.0 | None | None | 360 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 47 | 0 | 47 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `10`
- Gating Δ: `13244`
- No-generation Δ: `167833`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.2466, "current_avg_pnl": -1.4673, "current_win_rate": 0.0, "previous_avg_pnl": -1.2207, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 360, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::VOLUME_SURGE_BREAKOUT**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **EVAL::VOLUME_SURGE_BREAKOUT**
