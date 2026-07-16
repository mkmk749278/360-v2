# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `13761` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 352 | 352 | 243 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1648 | 1644 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1628 | 1629 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 1624 | 1532 | 95 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1629 | 1510 | 124 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 1641 | 1642 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1450 | 1450 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1634 | 1634 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 1634 | 1581 | 107 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 1698 | 1748 | 0 | 0 | 0 | 0 | non-generating (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 1648 | 1480 | 217 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 1548 | 1548 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1629 | 1629 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1622 | 1571 | 53 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1528 | 1607 | 13 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1431 | 1370 | 63 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 1433 | 1425 | 10 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1648 | 1648 | 0 | 0 | 0 | 0 | non-generating (basic_filters_failed) |
| EVAL::WHALE_MOMENTUM | 1450 | 1450 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 310 | 310 | 160 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 438 | 438 | 423 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 300 | 300 | 300 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 557 | 557 | 409 | 3 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 171 | 171 | 63 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 55 | 55 | 54 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 59 | 59 | 59 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1644): breakout_not_found=839, basic_filters_failed=653, breakout_stale=77, move_not_fresh=56, volume_spike_missing=13, retest_proximity_failed=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1629): cls_disabled_merged_into_lsr=1629
- **EVAL::DIVERGENCE_CONTINUATION** (total=1532): basic_filters_failed=561, cvd_divergence_failed=434, ema_alignment_reject=260, h1_trend_not_aligned=231, missing_fvg_or_orderblock=26, retest_proximity_failed=20
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1510): basic_filters_failed=551, auction_not_detected=377, tail_too_small=267, reclaim_hold_failed=249, regime_blocked=66
- **EVAL::FUNDING_EXTREME** (total=1642): funding_not_extreme=872, basic_filters_failed=497, missing_funding_rate=223, rsi_reject=42, ema_alignment_reject=8
- **EVAL::LIQUIDATION_REVERSAL** (total=1450): cascade_threshold_not_met=852, basic_filters_failed=559, cvd_divergence_failed=22, rsi_reject=13, missing_fvg_or_orderblock=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1634): no_ma_cross=1037, basic_filters_failed=562, ma_cross_cooldown=35
- **EVAL::MEAN_REVERT** (total=1581): no_extension=1171, basic_filters_failed=410
- **EVAL::MOVER_AVWAP_SCALP** (total=1748): basic_filters_failed=656, no_mover_leg=535, no_avwap_tag=372, avwap_reclaim_no_volume=114, avwap_slope_against=71
- **EVAL::MOVER_TREND_PULLBACK** (total=1480): basic_filters_failed=654, mover_run_too_small=529, no_reclaim=244, no_pullback_tag=53
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1548): feature_disabled=1548
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1629): regime_blocked=982, breakout_not_found=366, basic_filters_failed=174, adx_reject=105, ema_alignment_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1571): regime_blocked=710, basic_filters_failed=377, compression_not_detected=231, breakout_not_detected=196, rsi_reject=47, volume_confirmation_failed=10
- **EVAL::SR_FLIP_RETEST** (total=1607): basic_filters_failed=551, long_disabled=245, whipsaw_flip=233, retest_out_of_zone=167, long_break_volume_thin=157, flip_close_not_confirmed=141, regime_blocked=65, reclaim_hold_failed=40, long_acceptance_not_held=6, wick_quality_failed=2
- **EVAL::STANDARD** (total=1370): basic_filters_failed=364, momentum_reject=336, adx_reject=237, sweeps_not_detected=165, macd_reject=149, ema_alignment_reject=112, invalid_sl_geometry=7
- **EVAL::TREND_PULLBACK** (total=1425): h1_pullback_not_confirmed=392, basic_filters_failed=265, h1_trend_not_aligned=235, ema_alignment_reject=199, body_conviction_fail=99, ema_not_tested_prev=89, no_ema_reclaim_close=78, rsi_reject=55, prev_already_below_emas=6, prev_already_above_emas=4, momentum_flat=2, no_prev_high_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1648): basic_filters_failed=653, breakout_not_found=612, move_not_fresh=300, breakout_stale=78, retest_proximity_failed=5
- **EVAL::WHALE_MOMENTUM** (total=1450): momentum_reject=1101, recent_ticks_insufficient=258, basic_filters_failed=91

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 2713 | 33.5% |
| RANGING | 2303 | 28.5% |
| TRENDING_UP | 1707 | 21.1% |
| TRENDING_DOWN | 909 | 11.2% |
| VOLATILE | 459 | 5.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **197**
- Average confidence gap to threshold: **18.28** (samples=197) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=183, BZUSDT=14

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 83 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 15 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 100 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 12 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 19 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 9 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 170 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 14 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 100 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 83 | 45.76 | 65.00 | 19.24 | 19.85 | 20.00 | 17.00 | 0.00 | 21.60 |
| DIVERGENCE_CONTINUATION | kept | 15 | 79.30 | 65.00 | -14.30 | 20.69 | 20.00 | 16.30 | 5.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 112 | 48.72 | 65.00 | 16.28 | 19.95 | 19.74 | 20.00 | 1.05 | 24.82 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.00 | 65.00 | -2.00 | 20.40 | 18.00 | 20.00 | 6.00 | 1.70 |
| MOVER_AVWAP_SCALP | kept | 19 | 76.11 | 65.00 | -11.11 | 16.09 | 17.13 | 15.80 | 4.03 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 9 | 62.94 | 65.00 | 2.06 | 21.20 | 16.40 | 15.80 | 3.00 | 12.00 |
| MOVER_TREND_PULLBACK | kept | 170 | 77.28 | 65.00 | -12.28 | 18.55 | 17.67 | 15.80 | 4.00 | 0.07 |
| QUIET_COMPRESSION_BREAK | filtered | 14 | 51.38 | 65.00 | 13.62 | 20.15 | 19.86 | 20.00 | 0.00 | 20.03 |
| QUIET_COMPRESSION_BREAK | kept | 100 | 73.19 | 65.00 | -8.19 | 19.80 | 20.00 | 20.00 | 0.00 | 4.30 |
| SR_FLIP_RETEST | kept | 1 | 70.00 | 65.00 | -5.00 | 20.30 | 20.00 | 15.20 | 1.00 | -3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 83 | 45.76 | 17.00 | 8.00 | 13.16 | 14.00 | 8.50 | 6.70 | 0.00 |
| DIVERGENCE_CONTINUATION | kept | 15 | 79.30 | 25.00 | 18.00 | 9.00 | 10.00 | 5.00 | 7.30 | 5.00 |
| FAILED_AUCTION_RECLAIM | filtered | 112 | 48.72 | 17.00 | 14.43 | 12.16 | 14.00 | 8.12 | 6.76 | 1.05 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.00 | 25.00 | 18.00 | 3.00 | 5.00 | 5.00 | 6.70 | 6.00 |
| MOVER_AVWAP_SCALP | kept | 19 | 76.11 | 17.00 | 18.00 | 7.89 | 14.00 | 5.18 | 10.00 | 4.03 |
| MOVER_TREND_PULLBACK | filtered | 9 | 62.94 | 15.44 | 20.00 | 7.50 | 14.00 | 5.00 | 10.00 | 3.00 |
| MOVER_TREND_PULLBACK | kept | 170 | 77.28 | 17.05 | 18.01 | 7.99 | 14.14 | 6.16 | 10.00 | 4.00 |
| QUIET_COMPRESSION_BREAK | filtered | 14 | 51.38 | 17.00 | 18.00 | 12.86 | 14.00 | 7.25 | 2.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 100 | 73.19 | 17.00 | 18.00 | 13.29 | 14.00 | 8.50 | 6.70 | 0.00 |
| SR_FLIP_RETEST | kept | 1 | 70.00 | 17.00 | 18.00 | 3.00 | 14.00 | 8.00 | 9.00 | 1.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 83 | 45.76 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| DIVERGENCE_CONTINUATION | kept | 15 | 79.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 112 | 48.72 | 0.00 | 0.00 | 0.00 | 0.00 | 19.29 | 0.00 | 0.00 | 0.00 | **19.29** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 19 | 76.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 9 | 62.94 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_TREND_PULLBACK | kept | 170 | 77.28 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.07** |
| QUIET_COMPRESSION_BREAK | filtered | 14 | 51.38 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 10.80 | **15.10** |
| QUIET_COMPRESSION_BREAK | kept | 100 | 73.19 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | kept | 1 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1046 (23.6%) | WOULD_LOSE=1274 | WOULD_EXPIRE=2111 | pending (awaiting window)=569

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| dispatch_cooldown | 18 | 94.4% | 0.0 | 7.2 | -0.40 | **INSUFFICIENT_SAMPLE** |
| dispatch_staleness | 637 | 60.6% | 70.0 | 446.1 | -0.59 | **DROP** |
| level_still_in_play | 1538 | 18.1% | 162.0 | 92.0 | +0.05 | **TUNE** |
| min_confidence | 1735 | 15.9% | 933.0 | 387.4 | +0.31 | **KEEP** |
| quiet_scalp_block | 298 | 6.0% | 16.0 | 26.9 | -0.04 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 26 | 7.7% | 6.0 | 1.4 | +0.18 | **KEEP** |
| shadow_unit:SHADOW_FUNDING_FADE | 23 | 39.1% | 14.0 | 6.7 | +0.32 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 103 | 26.2% | 68.0 | 39.3 | +0.28 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 53 | 64.2% | 5.0 | 95.5 | -1.71 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 14834 across 17 strategies; 323 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 4261 | 10/4251/0 | 45% | -0.11 | NY/MARKDOWN/EXPANDED/BTC_RISING (+1.24R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 2986 | 0/2986/0 | 42% | -0.13 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.54R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| FAILED_AUCTION_RECLAIM | 2346 | 5/2341/0 | 45% | +0.07 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 1644 | 2/1642/0 | 35% | -0.18 | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL (+0.94R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 829 | 0/0/829 | 52% | +0.44 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+0.68R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.56R) |
| QUIET_COMPRESSION_BREAK | 610 | 0/610/0 | 47% | +0.02 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | NY/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 581 | 0/0/581 | 55% | +0.84 | NY/RANGE/NORMAL/BTC_NEUTRAL (+2.05R) | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (-0.85R) |
| SHADOW_FUNDING_FADE | 474 | 0/0/474 | 43% | -0.25 | NY/MARKUP/NORMAL/BTC_NEUTRAL (+0.13R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 385 | 0/385/0 | 23% | -0.41 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.06R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 231 | 0/231/0 | 39% | -0.09 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.21R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.51R) |
| MOVER_AVWAP_SCALP | 141 | 4/137/0 | 12% | -0.78 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 101 | 0/101/0 | 47% | +0.27 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 95 | 1/94/0 | 5% | -0.74 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 78 | 0/0/78 | 45% | -0.09 | — | — |
| WHALE_MOMENTUM | 70 | 0/70/0 | 20% | -0.14 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.44R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.44R) |
| BREAKDOWN_SHORT | 1 | 1/0/0 | 100% | +1.50 | — | — |
| MA_CROSS_TREND_SHIFT | 1 | 0/1/0 | 0% | -0.64 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG); `SHADOW_RANGE_FADE @ NY/RANGE/NORMAL/BTC_NEUTRAL` +2.05R (n=25, STRONG); `SHADOW_RANGE_FADE @ NY/QUIET/COMPRESSED/BTC_NEUTRAL` +1.90R (n=15, STRONG)
- **Weakest cells**: `DIVERGENCE_CONTINUATION @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL` -1.00R (n=44, NEGATIVE); `DIVERGENCE_CONTINUATION @ NY/MARKDOWN/EXPANDED/BTC_RISING` -1.00R (n=41, NEGATIVE); `SR_FLIP_RETEST @ NY/MARKDOWN/CASCADE/BTC_NEUTRAL` -1.00R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FAILED_AUCTION_RECLAIM | 234 | 53% / +0.03R | 234 | 53% / +0.12R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 164 | 41% / -0.17R | 164 | 42% / -0.10R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 20 | 35% / -0.20R | 20 | 35% / -0.26R | -0.06 | **FIXED** |
| DIVERGENCE_CONTINUATION | 52 | 38% / -0.29R | 52 | 44% / -0.23R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 161 | 58% / +0.06R | 161 | 62% / +0.12R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 115 | 47% / +0.09R | 115 | 47% / +0.10R | +0.02 | **ATR** |
| WHALE_MOMENTUM | 8 | 25% / -0.04R | 8 | 25% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 9 | 67% / +0.19R | 9 | 67% / +0.14R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 6 | 50% / -0.04R | 6 | 50% / +0.09R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 6 | 83% / +0.26R | 6 | 83% / +0.21R | — | **MEASURING** |
| BREAKDOWN_SHORT | 1 | 0% / -0.07R | 1 | 0% / -0.04R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 1 | 0% / -1.00R | 1 | 100% / +0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 8 · alerting: **0** · boot grace active: True

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| btc_reference | ok | BTC ref 64636.20 | 0 |
| candle_coverage | ok | 83/84 symbols with ≥20 15m candles | 0 |
| geometry_ab | ok | boot grace (upstream +22 but output +0 (streak 1/6)) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_path | ok | output +137 / upstream +22 | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| strategy_edge | ok | output +4 / upstream +22 | 0 |
| suppression_audit | ok | output +22 / upstream +47 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `5621`
- `Path funnel` emissions: `1`
- `Regime distribution` emissions: `1`
- `QUIET_SCALP_BLOCK` events: `197`
- `confidence_gate` events: `525`
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
- cvd: presence[present=6548] state[populated=6548] buckets[many=6548] sources[none] quality[none]
- funding_rate: presence[absent=1085, present=5463] state[empty=1085, populated=5463] buckets[few=5463, none=1085] sources[none] quality[none]
- liquidation_clusters: presence[absent=5413, present=1135] state[empty=5413, populated=1135] buckets[few=1001, none=5413, some=134] sources[none] quality[none]
- oi_snapshot: presence[absent=403, present=6145] state[empty=403, populated=6145] buckets[many=6145, none=403] sources[none] quality[none]
- order_book: presence[absent=1077, present=5471] state[populated=5471, unavailable=1077] buckets[few=5471, none=1077] sources[book_ticker=5471, unavailable=1077] quality[none=1077, top_of_book_only=5471]
- orderblocks: presence[absent=6548] state[empty=6548] buckets[none=6548] sources[not_implemented=6548] quality[none]
- recent_ticks: presence[present=6548] state[populated=6548] buckets[many=6548] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.40605902671814` sec
- Median create→first breach: `12848.162561535835` sec
- Median create→terminal: `12859.845675468445` sec
- Median first breach→terminal: `2.5106139183044434` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.4056 | 16065.923423051834 | 16066.725338935852 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.7101 | 25069.295897960663 | 25072.613380908966 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | 0.9409 | 15358.421468019485 | 15360.125212907791 |
| MOVER_TREND_PULLBACK | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 3.4033 | 8994.417893886566 | 9170.084368944168 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 55 | 1 | 54 | 0.0 | 0.0 | None | None | 1 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 59 | 0 | 59 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-222`
- Gating Δ: `-149264`
- No-generation Δ: `-2311739`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0884, "current_avg_pnl": 0.9409, "current_win_rate": 33.3, "previous_avg_pnl": 1.0293, "previous_win_rate": 50.0, "win_rate_delta": -16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.6966, "current_avg_pnl": 3.4033, "current_win_rate": 0.0, "previous_avg_pnl": 1.7067, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -51, "geometry_changed_delta": 0, "geometry_preserved_delta": -7923, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -60, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
