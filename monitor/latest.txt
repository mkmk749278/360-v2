# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `11254` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 1815 | 1815 | 1643 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 7196 | 7196 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 7769 | 7770 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 7728 | 7274 | 495 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 7772 | 7519 | 266 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 7757 | 7695 | 64 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 6890 | 6891 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 7785 | 7786 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 7787 | 7555 | 250 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 7542 | 7623 | 245 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 7196 | 6563 | 976 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 7534 | 7534 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 7770 | 7772 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 7716 | 7644 | 83 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 7805 | 7621 | 225 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 7491 | 7481 | 233 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 6852 | 6538 | 329 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 6867 | 6796 | 75 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 7194 | 7196 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 6891 | 6892 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1081 | 1081 | 571 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 160 | 160 | 160 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 1272 | 1272 | 1270 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 257 | 257 | 257 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 257 | 257 | 257 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 2830 | 2830 | 1724 | 3 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 251 | 251 | 197 | 0 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 656 | 656 | 656 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 727 | 727 | 409 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 405 | 405 | 405 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=7196): breakout_not_found=3331, basic_filters_failed=2556, move_not_fresh=758, breakout_stale=323, retest_proximity_failed=226, volume_spike_missing=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=7770): cls_disabled_merged_into_lsr=7770
- **EVAL::DIVERGENCE_CONTINUATION** (total=7274): basic_filters_failed=2513, cvd_divergence_failed=2061, h1_trend_not_aligned=1750, ema_alignment_reject=787, retest_proximity_failed=131, missing_fvg_or_orderblock=32
- **EVAL::FAILED_AUCTION_RECLAIM** (total=7519): auction_not_detected=2693, basic_filters_failed=2273, reclaim_hold_failed=1087, tail_too_small=750, regime_blocked=716
- **EVAL::FUNDING_EXTREME** (total=7695): funding_not_extreme=4508, basic_filters_failed=2446, ema_alignment_reject=455, missing_funding_rate=189, momentum_reject=36, cvd_divergence_failed=30, rsi_reject=27, missing_fvg_or_orderblock=4
- **EVAL::LIQUIDATION_REVERSAL** (total=6891): cascade_threshold_not_met=4377, basic_filters_failed=2485, cvd_divergence_failed=20, rsi_reject=8, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=7786): no_ma_cross=5265, basic_filters_failed=2513, ma_cross_htf_misaligned=8
- **EVAL::MEAN_REVERT** (total=7555): no_extension=6770, basic_filters_failed=785
- **EVAL::MOVER_AVWAP_SCALP** (total=7623): basic_filters_failed=2581, no_mover_leg=2350, no_avwap_tag=1433, avwap_slope_against=714, avwap_reclaim_no_volume=437, no_avwap_reclaim=108
- **EVAL::MOVER_TREND_PULLBACK** (total=6563): mover_run_too_small=2800, basic_filters_failed=2569, no_reclaim=931, no_pullback_tag=263
- **EVAL::OPENING_RANGE_BREAKOUT** (total=7534): feature_disabled=7534
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=7772): regime_blocked=6075, breakout_not_found=880, adx_reject=535, basic_filters_failed=278, ema_alignment_reject=4
- **EVAL::QUIET_COMPRESSION_BREAK** (total=7644): regime_blocked=2405, basic_filters_failed=1995, compression_not_detected=1927, breakout_not_detected=1208, volume_confirmation_failed=65, rsi_reject=44
- **EVAL::RANGE_FADE** (total=7621): no_range_edge=6836, basic_filters_failed=785
- **EVAL::SR_FLIP_RETEST** (total=7481): basic_filters_failed=2272, flip_close_not_confirmed=1182, long_break_volume_thin=827, regime_blocked=714, whipsaw_flip=668, long_disabled=624, reclaim_hold_failed=606, retest_out_of_zone=429, wick_quality_failed=74, long_acceptance_not_held=32, ema_alignment_reject=27, rsi_reject=14, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=6538): adx_reject=3020, momentum_reject=1659, sweeps_not_detected=690, macd_reject=466, basic_filters_failed=453, ema_alignment_reject=215, invalid_sl_geometry=28, rsi_reject=7
- **EVAL::TREND_PULLBACK** (total=6796): h1_trend_not_aligned=2538, h1_pullback_not_confirmed=1531, basic_filters_failed=894, ema_alignment_reject=655, no_ema_reclaim_close=465, ema_not_tested_prev=361, body_conviction_fail=145, rsi_reject=89, no_prev_low_break=46, prev_already_below_emas=23, prev_already_above_emas=22, no_prev_high_break=14, momentum_flat=5, ema21_not_tagged=5, momentum_reject=2, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=7196): breakout_not_found=3142, basic_filters_failed=2556, move_not_fresh=1109, breakout_stale=253, retest_proximity_failed=120, volume_spike_missing=11, missing_fvg_or_orderblock=5
- **EVAL::WHALE_MOMENTUM** (total=6892): momentum_reject=4886, recent_ticks_insufficient=1345, basic_filters_failed=661

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=110): setup_compat:regime_VOLATILE_UNSUITABLE=74, setup_compat:regime_BREAKOUT_EXPANSION=30, context_floor=6
- **FAILED_AUCTION_RECLAIM** (total=272): context_floor=121, setup_compat:regime_STRONG_TREND=115, execution:overextended=36
- **FUNDING_EXTREME_SIGNAL** (total=160): execution:trigger_not_confirmed=160
- **LIQUIDITY_SWEEP_REVERSAL** (total=434): execution:trigger_not_confirmed=243, execution:overextended=119, setup_compat:regime_STRONG_TREND=72
- **MEAN_REVERT** (total=83): execution:overextended=83
- **MOVER_AVWAP_SCALP** (total=257): execution:trigger_not_confirmed=257
- **MOVER_TREND_PULLBACK** (total=1720): execution:trigger_not_confirmed=1344, execution:overextended=376
- **QUIET_COMPRESSION_BREAK** (total=37): context_floor=37
- **RANGE_FADE** (total=157): setup_compat:regime_VOLATILE_UNSUITABLE=77, setup_compat:regime_WEAK_TREND=45, setup_compat:regime_STRONG_TREND=18, execution:overextended=17
- **TREND_PULLBACK_EMA** (total=323): setup_compat:regime_CLEAN_RANGE=245, setup_compat:regime_DIRTY_RANGE=40, setup_compat:regime_VOLATILE_UNSUITABLE=38

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 16836 | 43.9% |
| RANGING | 9640 | 25.1% |
| TRENDING_DOWN | 5096 | 13.3% |
| TRENDING_UP | 3808 | 9.9% |
| VOLATILE | 2983 | 7.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **38**
- Average confidence gap to threshold: **15.54** (samples=38) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HYPEUSDT=10, FILUSDT=10, BNBUSDT=6, XLMUSDT=6, WLFIUSDT=4, ETCUSDT=1, PUMPUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 6 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 3 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 882 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 17 |
| SR_FLIP_RETEST | filtered | min_confidence | 17 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 112 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 4 | 58.30 | 63.75 | 5.45 | 20.73 | 20.00 | 15.80 | 5.00 | 11.00 |
| FAILED_AUCTION_RECLAIM | filtered | 6 | 56.48 | 65.00 | 8.52 | 21.83 | 20.00 | 20.00 | 3.75 | 21.60 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.15 | 65.00 | -1.15 | 19.20 | 20.00 | 20.00 | 4.75 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 3 | 72.60 | 65.00 | -7.60 | 21.23 | 19.40 | 17.00 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 4 | 64.90 | 65.00 | 0.10 | 21.20 | 18.50 | 15.80 | 3.50 | 21.60 |
| MOVER_TREND_PULLBACK | kept | 882 | 77.53 | 65.00 | -12.53 | 19.39 | 18.89 | 15.80 | 4.41 | 0.96 |
| QUIET_COMPRESSION_BREAK | filtered | 17 | 38.99 | 65.00 | 26.01 | 19.91 | 20.00 | 20.00 | 0.00 | 13.65 |
| SR_FLIP_RETEST | filtered | 28 | 58.01 | 62.57 | 4.56 | 21.31 | 19.80 | 15.26 | 2.77 | 14.38 |
| SR_FLIP_RETEST | kept | 112 | 70.20 | 65.00 | -5.20 | 19.75 | 19.99 | 15.29 | 1.78 | 0.68 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 4 | 58.30 | 25.00 | 8.00 | 6.00 | 14.00 | 5.00 | 6.30 | 5.00 |
| FAILED_AUCTION_RECLAIM | filtered | 6 | 56.48 | 18.33 | 14.00 | 12.00 | 12.00 | 10.00 | 8.00 | 3.75 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.15 | 21.00 | 16.00 | 3.00 | 12.00 | 3.75 | 5.65 | 4.75 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 3 | 72.60 | 25.00 | 14.00 | 4.00 | 11.00 | 7.17 | 8.43 | 3.00 |
| MOVER_TREND_PULLBACK | filtered | 4 | 64.90 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 9.00 | 3.50 |
| MOVER_TREND_PULLBACK | kept | 882 | 77.53 | 22.26 | 18.04 | 8.04 | 12.22 | 5.65 | 7.87 | 4.41 |
| QUIET_COMPRESSION_BREAK | filtered | 17 | 38.99 | 17.00 | 18.00 | 10.94 | 14.00 | 5.21 | 2.50 | 0.00 |
| SR_FLIP_RETEST | filtered | 28 | 58.01 | 24.14 | 14.07 | 4.50 | 13.25 | 5.88 | 7.79 | 2.77 |
| SR_FLIP_RETEST | kept | 112 | 70.20 | 20.79 | 16.84 | 4.45 | 13.87 | 5.67 | 8.23 | 1.78 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 4 | 58.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 6 | 56.48 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 3 | 72.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 4 | 64.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MOVER_TREND_PULLBACK | kept | 882 | 77.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **0.96** |
| QUIET_COMPRESSION_BREAK | filtered | 17 | 38.99 | 0.00 | 0.00 | 0.00 | 0.00 | 2.78 | 0.00 | 0.00 | 6.99 | **9.77** |
| SR_FLIP_RETEST | filtered | 28 | 58.01 | 0.00 | 0.00 | 0.00 | 0.00 | 8.49 | 0.00 | 0.00 | 0.00 | **8.49** |
| SR_FLIP_RETEST | kept | 112 | 70.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.26** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=714 (17.7%) | WOULD_LOSE=1155 | WOULD_EXPIRE=2170 | pending (awaiting window)=961

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 128 | 36.7% | 72.6 | 71.8 | +0.01 | **TUNE** |
| context_floor:FAILED_AUCTION_RECLAIM | 465 | 0.0% | 115.5 | 0.0 | +0.25 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 112 | 0.0% | 16.5 | 0.0 | +0.15 | **KEEP** |
| context_floor:VOLUME_SURGE_BREAKOUT | 1 | 0.0% | 0.2 | 0.0 | +0.17 | **INSUFFICIENT_SAMPLE** |
| data_stale | 1 | 100.0% | 0.0 | 0.3 | -0.26 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 65 | 0.0% | 11.5 | 0.0 | +0.18 | **KEEP** |
| dispatch_staleness_v2 | 583 | 20.4% | 137.7 | 54.9 | +0.14 | **KEEP** |
| level_still_in_play | 957 | 13.7% | 311.6 | 45.7 | +0.28 | **KEEP** |
| min_confidence | 1243 | 23.3% | 804.8 | 333.0 | +0.38 | **KEEP** |
| quiet_scalp_block | 292 | 14.4% | 137.2 | 41.1 | +0.33 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 5 | 20.0% | 2.1 | 0.8 | +0.26 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 58 | 74.1% | 16.2 | 30.9 | -0.25 | **DROP** |
| shadow_unit:SHADOW_MEAN_REVERT | 42 | 19.0% | 30.8 | 19.2 | +0.28 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 87 | 36.8% | 31.0 | 76.9 | -0.53 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 65017 across 20 strategies; 1480 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 14781 | 48/14733/0 | 62% | +0.20 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.13R) |
| FAILED_AUCTION_RECLAIM | 11621 | 24/11597/0 | 52% | +0.04 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 10949 | 2/10947/0 | 43% | -0.19 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.14R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.30R) |
| DIVERGENCE_CONTINUATION | 5766 | 6/5760/0 | 47% | -0.06 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.22R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| QUIET_COMPRESSION_BREAK | 4595 | 0/4595/0 | 47% | +0.03 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MEAN_REVERT | 2999 | 0/2999/0 | 80% | +0.60 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_MEAN_REVERT | 2799 | 0/0/2799 | 38% | -0.06 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.82R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_RANGE_FADE | 2443 | 0/0/2443 | 35% | +0.10 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.30R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 2435 | 5/2430/0 | 44% | -0.07 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| RANGE_FADE | 1804 | 0/1804/0 | 3% | -0.98 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.21R) |
| SHADOW_FUNDING_FADE | 1642 | 0/0/1642 | 37% | -0.35 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.52R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 1043 | 12/1031/0 | 38% | -0.08 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 625 | 0/625/0 | 41% | -0.21 | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.36R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 306 | 2/304/0 | 36% | -0.08 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| MOVER_AVWAP_SCALP | 275 | 18/257/0 | 36% | -0.33 | NY/MARKUP/CASCADE/BTC_FALLING (+0.55R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 239 | 5/234/0 | 54% | +0.31 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 208 | 0/0/208 | 46% | -0.11 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.03R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 11 | 0/11/0 | 36% | -0.62 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +1.95R (n=34, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.30R (n=50, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.30R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 31 | 42% / +0.14R | 31 | 32% / -0.15R | -0.30 | **FIXED** |
| TREND_PULLBACK_EMA | 23 | 52% / -0.16R | 23 | 57% / +0.05R | +0.21 | **ATR** |
| MOVER_AVWAP_SCALP | 47 | 43% / -0.08R | 47 | 53% / +0.05R | +0.14 | **ATR** |
| MEAN_REVERT | 235 | 58% / +0.15R | 235 | 56% / +0.28R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| SR_FLIP_RETEST | 1546 | 47% / -0.10R | 1546 | 50% / -0.03R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 267 | 50% / -0.08R | 267 | 55% / -0.03R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 646 | 45% / -0.02R | 646 | 44% / -0.04R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 304 | 50% / -0.02R | 304 | 56% / +0.00R | +0.02 | **ATR** |
| MOVER_TREND_PULLBACK | 1381 | 59% / +0.09R | 1381 | 62% / +0.07R | -0.02 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 1370 | 50% / -0.02R | 1370 | 49% / -0.01R | +0.01 | **ATR** |
| RANGE_FADE | 137 | 2% / -1.04R | 137 | 2% / -1.04R | +0.01 | **ATR** |
| BREAKDOWN_SHORT | 8 | 25% / -0.27R | 8 | 25% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 4 | 0% / -1.12R | 4 | 50% / -0.27R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 2 | 50% / -0.02R | 2 | 50% / -0.33R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 3 | 67% / +0.16R | 3 | 67% / +0.06R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 206 | 29% | -0.11R | 66 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 37 | 54% | +0.04R | 27 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 2 | 0% | -0.15R | 2 | MEASURING |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 18 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=-0.43R (bound 0.3) (streak 7/6) (sustained 7 cycles)
- **ALERT** `mean_revert_emission` — 242 detections since last emission (emitted_total=0) — check gate rejections (streak 7/6) (sustained 7 cycles)
- **ALERT** `range_fade_emission` — 610 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 7/6) (sustained 7 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64067.60 | 0 |
| candle_coverage | ok | 79/80 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +79 / upstream +45 | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=-0.43R (bound 0.3) (streak 7/6) | 7 |
| emission_controller | ok | last cycle 1s ago; live_overrides=16 | 0 |
| gate_override_shadow | ok | output +1 / upstream +1 | 0 |
| geometry_ab | ok | output +2 / upstream +78 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 242 detections since last emission (emitted_total=0) — check gate rejections (streak 7/6) | 7 |
| mean_revert_path | ok | output +27 / upstream +78 | 0 |
| range_fade_emission | violating | 610 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 7/6) | 7 |
| range_fade_path | ok | output +65 / upstream +78 | 0 |
| shadow_units | ok | last shadow stamp 5m ago | 0 |
| staleness_v2_shadow | ok | output +1 / upstream +1 | 0 |
| strategy_edge | ok | output +215 / upstream +78 | 0 |
| suppression_audit | ok | output +78 / upstream +45 | 0 |
| tuned_variants | ok | seen=712 stamped=7 skipped=705 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `14839`
- `Path funnel` emissions: `5`
- `Regime distribution` emissions: `5`
- `QUIET_SCALP_BLOCK` events: `38`
- `confidence_gate` events: `1058`
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
- cvd: presence[present=31244] state[populated=31244] buckets[many=31244] sources[none] quality[none]
- funding_rate: presence[absent=1249, present=29995] state[empty=1249, populated=29995] buckets[few=29995, none=1249] sources[none] quality[none]
- liquidation_clusters: presence[absent=20952, present=10292] state[empty=20952, populated=10292] buckets[few=8092, none=20952, some=2200] sources[none] quality[none]
- oi_snapshot: presence[absent=631, present=30613] state[empty=631, populated=30613] buckets[many=30613, none=631] sources[none] quality[none]
- order_book: presence[absent=7546, present=23698] state[populated=23698, unavailable=7546] buckets[few=23698, none=7546] sources[book_ticker=23698, unavailable=7546] quality[none=7546, top_of_book_only=23698]
- orderblocks: presence[absent=31244] state[empty=31244] buckets[none=31244] sources[not_implemented=31244] quality[none]
- recent_ticks: presence[absent=499, present=30745] state[empty=499, populated=30745] buckets[many=30745, none=499] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.631224989891052` sec
- Median create→first breach: `3532.1583124399185` sec
- Median create→terminal: `3533.3669559955597` sec
- Median first breach→terminal: `5.045694470405579` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 2.1903 | 8542.849162101746 | 8550.52778506279 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.6687 | 2199.144641160965 | 2223.826686143875 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 378.4088189601898 | 379.6638000011444 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 4.4924 | 717.0642840862274 | 724.9684069156647 |
| MOVER_TREND_PULLBACK | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.1637 | 12128.890217065811 | 12131.302983045578 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.1 | 2238.6978158950806 | 2239.3980309963226 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 727 | 3 | 409 | 0.0 | 0.0 | None | None | 318 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 405 | 0 | 405 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-369`
- Gating Δ: `-158322`
- No-generation Δ: `-2146474`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 2.657, "current_avg_pnl": 2.1903, "current_win_rate": 33.3, "previous_avg_pnl": -0.4667, "previous_win_rate": 33.3, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 5.0476, "current_avg_pnl": 4.4924, "current_win_rate": 0.0, "previous_avg_pnl": -0.5552, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.3843, "current_avg_pnl": -2.1637, "current_win_rate": 0.0, "previous_avg_pnl": -0.7794, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -171, "geometry_changed_delta": 0, "geometry_preserved_delta": -10002, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -45, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
