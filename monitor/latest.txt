# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `5119` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 6798 | 6798 | 6650 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 36642 | 36643 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 29485 | 29485 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 29416 | 27926 | 1558 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 29489 | 28820 | 680 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 30020 | 29980 | 43 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 28300 | 28301 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 29500 | 29505 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 29505 | 28583 | 1289 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 37409 | 38307 | 410 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 36643 | 33844 | 3553 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 29960 | 29960 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 29487 | 29489 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 29410 | 29280 | 137 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 29873 | 29012 | 1091 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 29345 | 29201 | 202 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 27638 | 26070 | 1634 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 27704 | 27550 | 160 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 36635 | 36622 | 19 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 28301 | 28289 | 22 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1690 | 1690 | 1328 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 223 | 223 | 122 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 9343 | 9343 | 8956 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 3902 | 3902 | 3664 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1115 | 1115 | 881 | 4 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 11373 | 11373 | 9441 | 16 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1062 | 1062 | 1027 | 4 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3231 | 3231 | 3231 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 465 | 465 | 310 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 851 | 851 | 851 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 47 | 47 | 47 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2194 | 2194 | 1800 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=36643): breakout_not_found=16379, basic_filters_failed=10211, move_not_fresh=5858, breakout_stale=2308, volume_spike_missing=1183, retest_proximity_failed=704
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=29485): cls_disabled_merged_into_lsr=29485
- **EVAL::DIVERGENCE_CONTINUATION** (total=27926): cvd_divergence_failed=11085, basic_filters_failed=7645, h1_trend_not_aligned=6597, ema_alignment_reject=2349, missing_fvg_or_orderblock=157, retest_proximity_failed=93
- **EVAL::FAILED_AUCTION_RECLAIM** (total=28820): auction_not_detected=18198, basic_filters_failed=7423, reclaim_hold_failed=1563, regime_blocked=990, tail_too_small=615, rsi_reject=31
- **EVAL::FUNDING_EXTREME** (total=29980): funding_not_extreme=20182, basic_filters_failed=8017, missing_funding_rate=1259, ema_alignment_reject=344, rsi_reject=87, momentum_reject=71, cvd_divergence_failed=20
- **EVAL::LIQUIDATION_REVERSAL** (total=28301): cascade_threshold_not_met=20186, basic_filters_failed=8028, cvd_divergence_failed=52, rsi_reject=35
- **EVAL::MA_CROSS_TREND_SHIFT** (total=29505): no_ma_cross=21239, basic_filters_failed=7645, ma_cross_htf_misaligned=621
- **EVAL::MEAN_REVERT** (total=28583): no_extension=21305, basic_filters_failed=7278
- **EVAL::MOVER_AVWAP_SCALP** (total=38307): no_mover_leg=13770, no_avwap_tag=10483, basic_filters_failed=10235, avwap_slope_against=2608, avwap_reclaim_no_volume=799, no_avwap_reclaim=394, anchor_too_recent=18
- **EVAL::MOVER_TREND_PULLBACK** (total=33844): mover_run_too_small=17383, basic_filters_failed=10223, no_reclaim=5390, no_pullback_tag=848
- **EVAL::OPENING_RANGE_BREAKOUT** (total=29960): feature_disabled=29960
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=29489): regime_blocked=22832, breakout_not_found=3242, basic_filters_failed=2795, adx_reject=612, ema_alignment_reject=8
- **EVAL::QUIET_COMPRESSION_BREAK** (total=29280): compression_not_detected=10506, regime_blocked=7639, breakout_not_detected=4852, basic_filters_failed=4628, macd_reject=1123, volume_confirmation_failed=495, missing_fvg_or_orderblock=23, rsi_reject=14
- **EVAL::RANGE_FADE** (total=29012): no_range_edge=21735, basic_filters_failed=7277
- **EVAL::SR_FLIP_RETEST** (total=29201): flip_close_not_confirmed=18029, basic_filters_failed=7422, regime_blocked=988, retest_out_of_zone=936, long_break_volume_thin=767, reclaim_hold_failed=617, h1_break_not_confirmed=247, wick_quality_failed=118, missing_fvg_or_orderblock=36, ema_alignment_reject=32, long_acceptance_not_held=9
- **EVAL::STANDARD** (total=26070): adx_reject=7237, basic_filters_failed=6371, momentum_reject=5358, sweeps_not_detected=2627, macd_reject=2252, ema_alignment_reject=1308, htf_poi_unanchored=856, rsi_reject=26, invalid_sl_geometry=21, mtf_reject=14
- **EVAL::TREND_PULLBACK** (total=27550): h1_trend_not_aligned=8878, h1_pullback_not_confirmed=5946, basic_filters_failed=3803, ema_alignment_reject=3578, no_ema_reclaim_close=2060, rsi_reject=921, ema_not_tested_prev=859, body_conviction_fail=838, prev_already_above_emas=218, no_prev_high_break=157, momentum_flat=118, prev_already_below_emas=114, no_prev_low_break=54, momentum_reject=3, missing_fvg_or_orderblock=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=36622): breakout_not_found=21439, basic_filters_failed=10211, move_not_fresh=2305, breakout_stale=1217, volume_spike_missing=1120, retest_proximity_failed=325, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=28289): momentum_reject=20627, recent_ticks_insufficient=5883, basic_filters_failed=1779

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=365): setup_compat:regime_VOLATILE_UNSUITABLE=365
- **FAILED_AUCTION_RECLAIM** (total=322): execution:overextended=203, context_floor=119
- **FUNDING_EXTREME_SIGNAL** (total=206): execution:trigger_not_confirmed=192, context_floor=14
- **LIQUIDITY_SWEEP_REVERSAL** (total=2000): execution:trigger_not_confirmed=1349, execution:overextended=348, setup_compat:regime_STRONG_TREND=303
- **MEAN_REVERT** (total=1230): setup_compat:regime_WEAK_TREND=1009, setup_compat:regime_STRONG_TREND=221
- **MOVER_AVWAP_SCALP** (total=531): execution:overextended=465, execution:trigger_not_confirmed=57, entry_quality=9
- **MOVER_TREND_PULLBACK** (total=3671): execution:trigger_not_confirmed=2000, execution:overextended=1260, entry_quality=411
- **RANGE_FADE** (total=2161): setup_compat:regime_STRONG_TREND=1111, setup_compat:regime_WEAK_TREND=555, execution:overextended=468, setup_compat:regime_BREAKOUT_EXPANSION=24, setup_compat:regime_VOLATILE_UNSUITABLE=3
- **TREND_PULLBACK_EMA** (total=849): setup_compat:regime_CLEAN_RANGE=493, setup_compat:regime_DIRTY_RANGE=321, setup_compat:regime_VOLATILE_UNSUITABLE=35
- **VOLUME_SURGE_BREAKOUT** (total=25): execution:overextended=25
- **WHALE_MOMENTUM** (total=2130): execution:trigger_not_confirmed=2130

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 87550 | 45.8% |
| RANGING | 58134 | 30.4% |
| TRENDING_DOWN | 24480 | 12.8% |
| TRENDING_UP | 11551 | 6.0% |
| VOLATILE | 9600 | 5.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **48**
- Average confidence gap to threshold: **14.42** (samples=48) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=17, TAOUSDT=7, BTCUSDT=6, ARBUSDT=5, SOXLUSDT=4, AAOIUSDT=3, FETUSDT=3, PUMPUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 22 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 12 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 14 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 28 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 101 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 56 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 7 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 86 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 653 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 22 | 59.30 | 65.00 | 5.70 | 19.64 | 20.00 | 16.90 | 2.00 | 6.00 |
| DIVERGENCE_CONTINUATION | kept | 12 | 72.00 | 65.00 | -7.00 | 18.43 | 20.00 | 17.00 | 0.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 50.04 | 65.00 | 14.96 | 21.70 | 19.68 | 20.00 | 2.57 | 18.20 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 56.30 | 61.00 | 4.70 | 20.30 | 20.00 | 17.00 | 0.00 | 16.20 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 71.30 | 65.00 | -6.30 | 18.82 | 20.00 | 17.00 | 0.00 | 1.20 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 28 | 51.90 | 65.00 | 13.10 | 22.07 | 18.47 | 17.68 | 2.79 | 9.66 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 101 | 67.15 | 65.00 | -2.15 | 22.41 | 19.85 | 18.69 | 1.99 | -0.65 |
| MOVER_AVWAP_SCALP | filtered | 56 | 59.24 | 65.00 | 5.76 | 20.95 | 13.26 | 15.80 | 4.95 | 20.00 |
| MOVER_AVWAP_SCALP | kept | 7 | 79.57 | 65.00 | -14.57 | 20.39 | 17.06 | 15.80 | 4.36 | 3.29 |
| MOVER_TREND_PULLBACK | filtered | 86 | 60.56 | 65.00 | 4.44 | 19.37 | 19.18 | 15.80 | 4.31 | 19.55 |
| MOVER_TREND_PULLBACK | kept | 653 | 77.52 | 65.00 | -12.52 | 20.66 | 19.43 | 15.80 | 4.11 | -0.00 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 74.03 | 65.00 | -9.03 | 22.03 | 19.60 | 20.00 | 0.00 | 4.85 |
| SR_FLIP_RETEST | kept | 1 | 62.00 | 65.00 | 3.00 | 21.20 | 20.00 | 15.20 | 1.00 | 3.00 |
| WHALE_MOMENTUM | filtered | 6 | 45.70 | 65.00 | 19.30 | 22.33 | 14.00 | 17.00 | 0.00 | 23.30 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 22 | 59.30 | 17.00 | 18.00 | 3.00 | 10.00 | 8.00 | 7.30 | 2.00 |
| DIVERGENCE_CONTINUATION | kept | 12 | 72.00 | 25.00 | 8.00 | 6.00 | 14.00 | 9.00 | 10.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 50.04 | 18.71 | 14.00 | 3.43 | 13.43 | 8.75 | 7.35 | 2.57 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 56.30 | 25.00 | 18.00 | 3.00 | 14.00 | 2.50 | 10.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 71.30 | 25.00 | 18.00 | 3.00 | 14.00 | 2.50 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 28 | 51.90 | 23.29 | 14.00 | 6.75 | 13.50 | 6.32 | 4.56 | 2.79 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 101 | 67.15 | 22.31 | 14.04 | 4.04 | 12.67 | 5.65 | 6.44 | 1.99 |
| MOVER_AVWAP_SCALP | filtered | 56 | 59.24 | 19.00 | 18.00 | 11.14 | 12.00 | 5.00 | 9.15 | 4.95 |
| MOVER_AVWAP_SCALP | kept | 7 | 79.57 | 19.29 | 18.00 | 12.43 | 13.29 | 6.50 | 9.00 | 4.36 |
| MOVER_TREND_PULLBACK | filtered | 86 | 60.56 | 21.09 | 18.00 | 7.50 | 16.37 | 2.91 | 9.93 | 4.31 |
| MOVER_TREND_PULLBACK | kept | 653 | 77.52 | 19.19 | 18.00 | 7.53 | 12.62 | 7.24 | 8.84 | 4.11 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 74.03 | 19.00 | 17.00 | 12.75 | 14.00 | 7.62 | 8.50 | 0.00 |
| SR_FLIP_RETEST | kept | 1 | 62.00 | 17.00 | 18.00 | 3.00 | 11.00 | 5.00 | 10.00 | 1.00 |
| WHALE_MOMENTUM | filtered | 6 | 45.70 | 17.00 | 8.00 | 13.50 | 14.00 | 8.50 | 8.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 22 | 59.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 12 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 50.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 56.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 15.00 | 0.00 | 0.00 | **15.00** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 71.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 28 | 51.90 | 0.00 | 0.00 | 0.00 | 0.00 | 7.71 | 0.00 | 0.00 | 0.00 | **7.71** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 101 | 67.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 56 | 59.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 7 | 79.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 86 | 60.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0.00 | 0.00 | **0.35** |
| MOVER_TREND_PULLBACK | kept | 653 | 77.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 4 | 74.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 1 | 62.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 6 | 45.70 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **10.80** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- _no classified suppressed candidates yet — candidates classify after their validity window (~1h) of real candles has accumulated_

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
_**`suppressed` here means POST-SCORING suppressions only.** `suppression_audit.feeds_edge_matrix` returns False for every pre-scoring reject — `setup_compat:*` and `execution:*` fire ahead of the scoring engine and would swamp the matrix with a differently-measured population (~38k/window against ~4.5k) that Layer C's emission floor reads LIVE.  Those candidates are measured **in the dark lane instead** (`/signals/dark-live`), and the two populations are therefore **disjoint** — every dark row carries a `setup_compat:*` or `execution:*` gate, and none of them can appear here.  A path can read positive on this table and negative in the dark feed with no contradiction, because they are not measuring the same candidates.  Stated on the surface rather than in a docstring because reading one as a check on the other is a mistake this repo has now made (2026-08-04)._
_**Every cell is a 50-outcome ring** (`STRATEGY_EDGE_WINDOW`), so `n` is `min(seen, 50)` and `seen` is the denominator: a saturated cell is a rolling most-recent-50 window while a sparse cell beside it is all-time.  `sampled` counts cells that have evicted at least once._
- Outcomes recorded: **128317 held of 418857 seen** across 21 strategies; 2936 cells past the sample floor; **1419 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 41322 | 596/40726/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.17R) |
| MOVER_AVWAP_SCALP | 16580 | 174/16406/0 | 40% | -0.27 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10166 | 116/10050/0 | 41% | -0.23 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 8619 | 53/8566/0 | 49% | -0.04 | NY/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (+1.39R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 7354 | 28/7326/0 | 43% | -0.17 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6513 | 0/0/6513 | 44% | -0.08 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.83R) |
| SHADOW_RANGE_FADE | 5767 | 0/0/5767 | 37% | -0.07 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.63R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| QUIET_COMPRESSION_BREAK | 5390 | 324/5066/0 | 48% | -0.11 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.59R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| LIQUIDITY_SWEEP_REVERSAL | 5330 | 70/5260/0 | 37% | -0.48 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_FUNDING_FADE | 5069 | 0/0/5069 | 34% | -0.40 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3401 | 2/3399/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2918 | 35/2883/0 | 44% | -0.21 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 2385 | 0/2385/0 | 39% | -0.10 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2352 | 2/2350/0 | 31% | -0.46 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SR_FLIP_RETEST | 2064 | 11/2053/0 | 48% | -0.21 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| RANGE_FADE | 1142 | 4/1138/0 | 42% | -0.34 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1012 | 0/0/1012 | 55% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.19R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 82 | 12/70/0 | 46% | -0.08 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 170 | 27% / -0.58R | 170 | 49% / -0.17R | +0.41 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 600 | 43% / -0.23R | 600 | 56% / -0.03R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 990 | 46% / -0.30R | 990 | 55% / -0.14R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 1373 | 43% / -0.20R | 1373 | 49% / -0.08R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 369 | 44% / -0.33R | 369 | 46% / -0.22R | +0.10 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 122 | 37% / -0.16R | 122 | 47% / -0.06R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6457 | 49% / -0.12R | 6457 | 54% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 983 | 41% / -0.23R | 983 | 43% / -0.13R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 199 | 48% / -0.24R | 199 | 50% / -0.16R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 876 | 48% / -0.11R | 876 | 54% / -0.05R | +0.07 | **ATR** |
| MA_CROSS_TREND_SHIFT | 25 | 44% / -0.16R | 25 | 44% / -0.13R | +0.03 | **ATR** |
| RANGE_FADE | 50 | 36% / -0.33R | 50 | 38% / -0.34R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 874 | 46% / -0.15R | 874 | 46% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 218 | 52% / -0.07R | 218 | 51% / -0.07R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9225 | 30% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1373 | 47% | -0.08R | 206 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 76 | 50% | -0.06R | 50 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 804 | 37% / -0.15R | +0.92 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 976 | 40% / -0.25R | +0.76 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1779 | 34% / -0.10R | +0.74 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8275 | 36% / -0.16R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 973 | 39% / -0.03R | +0.25 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 142 | 36% / -0.33R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 851 | 35% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 795 | 34% / -0.18R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 180 | 30% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 224 | 28% / -0.64R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 181 | 55% / +0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 38 | 32% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 198 | 31% / -0.49R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 39 | 26% / -0.48R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 11 | 45% / +0.67R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **7** · boot grace active: False
- **ALERT** `geometry_ab` — upstream +356 but output +0 (streak 15/6) (sustained 15 cycles)
- **ALERT** `sar_exit_shadow` — upstream +356 but output +0 (streak 15/6) (sustained 15 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×597]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 37/6) (sustained 37 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=115, profile_reject=15. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 26/6) (sustained 26 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 37/6) (sustained 37 cycles)
- **ALERT** `tuned_variants` — 31 non-stamps — atr_arm_uncomputable=31 (seen=659 stamped=36 skipped=592) (streak 32/6) (sustained 32 cycles)
- **ALERT** `auto_dispatch` — 7 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=7) (streak 26/3) (sustained 26 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 39 fed / 0 quiet / 1 never delivered of 40 subscribed; 2422792 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 6 arms current, none stalled; covering 1205/1205 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 12 arms current, none stalled; covering 1041/1041 signals (100%) | 0 |
| auto_dispatch | violating | 7 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=7) (streak 26/3) | 26 |
| binance_ip_weight | ok | peak 313/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 85270.90 | 0 |
| candle_coverage | ok | 95/95 symbols with ≥20 15m candles, 95/95 updated within 45m [fresh=95; 75 Tier-1 futures + 20 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 0 dup bars, 0 undedupable; ws 0 out-of-order, 329 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 45 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | violating | upstream +45 but output +0 (streak 15/72) | 15 |
| dark_atr_trail_arms | ok | no open arms; covering 1128/1146 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 55 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1123/1141 signals (98%) | 0 |
| depth_feed | ok | 39/40 books fresh (stale 0, never 1, thin 0); 1020581 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 37/6) | 37 |
| emission_controller | ok | last cycle 0s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×597]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 37/6) | 37 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=115, profile_reject=15. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 26/6) | 26 |
| firestore_read_budget | ok | 1,392 reads/day of 50,000 [engine 1,343, signing 49]; top site keystore.roster_doc at 295/day (engine) | 0 |
| footprint_bars | ok | 4680 sealed bars over 39 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +356 but output +0 (streak 15/6) | 15 |
| indicator_cache_key | ok | 1924 frozen value(s) avoided; 0 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.21R over n=2883 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +274 / upstream +356 | 0 |
| mover_admission_metadata | ok | 920 symbols known, 213 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 20 held, 20 with scan counts, 20 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3074 rows held, 2335785 evicted (sampled: execution:trigger_not_confirmed 400/848785, execution:overextended 400/763232, setup_compat:regime_STRONG_TREND 400/358901) | 0 |
| price_action_lane | ok | 193329 evaluated, 93 emitted; layer1 93 stamped / 0 blind; cooldown=22989, delta_opposed=10990, no_footprint=58964, no_opposing_target=349, no_sweep=89982, rr_below_floor=9962 | 0 |
| promoted_pair_integrity | ok | 20/20 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.34R over n=1138 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +136 / upstream +356 | 0 |
| sar_alignment_crosscheck | ok | 0/1178 disagreed (0.0%) | 0 |
| sar_exit_shadow | violating | upstream +356 but output +0 (streak 15/6) | 15 |
| sar_hold_arm | ok | 1859 held arms settled, 141 unscored, 12 still walking (11 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 14/14 resolvable | 0 |
| sar_live_arms | ok | 12 arms current, none stalled; covering 1040/1040 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 73 records await one (14 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 5.71s, worst 42.34s over 2272 lifetime cycles; lifetime 0 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.98s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 86621 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 7m ago | 0 |
| snapshot_writer | ok | last cycle 23s ago (0.71s to run, worst 31.23s), 14 overrun(s) of 905 cycles, TTL 900s; slowest tickers=3.38s, signals=0.6s, activity=0.26s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +1 / upstream +356 | 0 |
| structural_snap | ok | 5922/5922 measured, 27 blind, 0 levels moved (refusals: redetect_cooldown=81) | 0 |
| structural_veto_lane | ok | 113 stamped; 0 with no readable level book, 0 with clear air ahead, 26 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +356 / upstream +45 | 0 |
| tuned_variants | violating | 31 non-stamps — atr_arm_uncomputable=31 (seen=659 stamped=36 skipped=592) (streak 32/6) | 32 |
| unlock_shorts | ok | 11 open, 44 scheduled, calendar 3.9h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `844002`
- `Path funnel` emissions: `23`
- `Regime distribution` emissions: `23`
- `QUIET_SCALP_BLOCK` events: `48`
- `confidence_gate` events: `996`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 1881 | 1881 | 1881 | 0 |
| futures_depth | 1 | 2566 | 2566 | 2566 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=163504] state[populated=163504] buckets[many=163504] sources[none] quality[none]
- funding_rate: presence[absent=22749, present=140755] state[empty=22749, populated=140755] buckets[few=140755, none=22749] sources[none] quality[none]
- liquidation_clusters: presence[absent=102697, present=60807] state[empty=102697, populated=60807] buckets[few=53764, none=102697, some=7043] sources[none] quality[none]
- oi_snapshot: presence[absent=17532, present=145972] state[empty=17532, populated=145972] buckets[many=145972, none=17532] sources[none] quality[none]
- order_book: presence[absent=41900, present=121604] state[populated=121604, unavailable=41900] buckets[few=121604, none=41900] sources[book_ticker=121604, unavailable=41900] quality[none=41900, top_of_book_only=121604]
- orderblocks: presence[absent=163504] state[empty=163504] buckets[none=163504] sources[measured_dark=163504] quality[none]
- recent_ticks: presence[present=163504] state[populated=163504] buckets[many=163504] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.90354585647583` sec
- Median create→first breach: `243468.34095096588` sec
- Median create→terminal: `243468.34099698067` sec
- Median first breach→terminal: `2.09808349609375e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 4 | 4 | 2.458462504126956 | 3.0 | 0.819487501375652 | 1 | 3 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 1.5727376274194331 | 1.572737711805074 | 1.0000000000000007 | 0 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | -0.9553 | 123459.63470542431 | 123459.63473892212 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.389 | 253610.71002388 | 253610.71004891396 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 465 | 1 | 310 | 0.0 | 0.0 | None | None | 155 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 851 | 0 | 851 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `29`
- Gating Δ: `38308`
- No-generation Δ: `576867`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.9553, "current_avg_pnl": -0.9553, "current_win_rate": 25.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 25.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.389, "current_avg_pnl": -1.389, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 155, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
