# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `4262` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 38 | 38 | 38 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 26445 | 26445 | 23718 | 31 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 153901 | 153909 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 147676 | 147686 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 147271 | 141502 | 6164 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 147716 | 141368 | 6670 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 150268 | 149835 | 475 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 134092 | 134106 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 148043 | 148070 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 148077 | 143078 | 6254 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 159991 | 165521 | 1383 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 153924 | 142368 | 17581 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 145564 | 145573 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 147688 | 147706 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 147212 | 146786 | 481 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 149338 | 145682 | 4865 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 142473 | 142123 | 5030 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 130847 | 123083 | 8204 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 131291 | 130549 | 795 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 153875 | 153901 | 1 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 134108 | 134126 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 24252 | 24252 | 18557 | 72 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2205 | 2205 | 1936 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 10 | 10 | 10 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 41584 | 41584 | 40852 | 15 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 10 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 14247 | 14247 | 13532 | 6 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3572 | 3572 | 2852 | 15 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 48176 | 48176 | 30227 | 323 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 52 | 52 | 51 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3076 | 3076 | 1631 | 33 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 11064 | 11064 | 10168 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 21588 | 21588 | 11686 | 108 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3887 | 3887 | 3790 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 11 | 11 | 10 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=153909): breakout_not_found=80050, basic_filters_failed=49001, move_not_fresh=16712, breakout_stale=5402, retest_proximity_failed=2477, volume_spike_missing=116, insufficient_candles=58, ema_alignment_reject=52, move_exhausted=33, rsi_reject=5, missing_fvg_or_orderblock=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=147686): cls_disabled_merged_into_lsr=147686
- **EVAL::DIVERGENCE_CONTINUATION** (total=141502): basic_filters_failed=45173, cvd_divergence_failed=40996, h1_trend_not_aligned=39896, ema_alignment_reject=12687, retest_proximity_failed=1906, missing_fvg_or_orderblock=569, regime_blocked=275
- **EVAL::FAILED_AUCTION_RECLAIM** (total=141368): auction_not_detected=50687, basic_filters_failed=44520, reclaim_hold_failed=24703, tail_too_small=17794, regime_blocked=3664
- **EVAL::FUNDING_EXTREME** (total=149835): funding_not_extreme=93953, basic_filters_failed=43920, missing_funding_rate=6082, ema_alignment_reject=3350, rsi_reject=1637, momentum_reject=443, cvd_divergence_failed=396, missing_fvg_or_orderblock=54
- **EVAL::LIQUIDATION_REVERSAL** (total=134106): cascade_threshold_not_met=87124, basic_filters_failed=45690, cvd_divergence_failed=693, rsi_reject=562, missing_fvg_or_orderblock=29, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=148070): no_ma_cross=100308, basic_filters_failed=45194, ma_cross_htf_misaligned=1676, ma_cross_cooldown=892
- **EVAL::MEAN_REVERT** (total=143078): no_extension=115634, basic_filters_failed=27053, insufficient_candles=391
- **EVAL::MOVER_AVWAP_SCALP** (total=165521): no_mover_leg=51793, no_avwap_tag=51303, basic_filters_failed=47868, avwap_slope_against=8413, avwap_reclaim_no_volume=2716, insufficient_candles=1719, no_avwap_reclaim=1687, anchor_too_recent=22
- **EVAL::MOVER_TREND_PULLBACK** (total=142368): mover_run_too_small=65360, basic_filters_failed=47334, no_reclaim=24031, no_pullback_tag=3424, insufficient_candles=2219
- **EVAL::OPENING_RANGE_BREAKOUT** (total=145573): feature_disabled=145573
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=147706): regime_blocked=93984, breakout_not_found=36456, basic_filters_failed=11002, adx_reject=6200, ema_alignment_reject=64
- **EVAL::QUIET_COMPRESSION_BREAK** (total=146786): regime_blocked=57249, basic_filters_failed=33500, compression_not_detected=31014, breakout_not_detected=23076, volume_confirmation_failed=1841, rsi_reject=67, missing_fvg_or_orderblock=26, macd_reject=13
- **EVAL::RANGE_FADE** (total=145682): no_range_edge=118010, basic_filters_failed=25779, insufficient_candles=1893
- **EVAL::SR_FLIP_RETEST** (total=142123): basic_filters_failed=44484, long_break_volume_thin=21354, whipsaw_flip=19261, flip_close_not_confirmed=18673, long_disabled=11874, reclaim_hold_failed=10293, retest_out_of_zone=8736, regime_blocked=3644, wick_quality_failed=2012, long_acceptance_not_held=903, missing_fvg_or_orderblock=497, ema_alignment_reject=372, rsi_reject=20
- **EVAL::STANDARD** (total=123083): momentum_reject=39915, adx_reject=35260, basic_filters_failed=19551, sweeps_not_detected=12994, macd_reject=7849, ema_alignment_reject=6803, rsi_reject=608, invalid_sl_geometry=92, mtf_reject=11
- **EVAL::TREND_PULLBACK** (total=130549): h1_trend_not_aligned=52014, basic_filters_failed=20017, h1_pullback_not_confirmed=17205, ema_alignment_reject=15245, ema_not_tested_prev=7201, no_ema_reclaim_close=7125, body_conviction_fail=4001, rsi_reject=3621, regime_blocked=1919, prev_already_below_emas=690, no_prev_high_break=502, prev_already_above_emas=432, no_prev_low_break=279, momentum_flat=191, missing_fvg_or_orderblock=67, momentum_reject=24, ema21_not_tagged=16
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=153901): breakout_not_found=75046, basic_filters_failed=48999, move_not_fresh=21419, breakout_stale=6205, retest_proximity_failed=1723, volume_spike_missing=324, rsi_reject=60, insufficient_candles=58, missing_fvg_or_orderblock=45, move_exhausted=15, ema_alignment_reject=7
- **EVAL::WHALE_MOMENTUM** (total=134126): momentum_reject=82964, recent_ticks_insufficient=35456, basic_filters_failed=15706

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=5): execution:overextended=5
- **DIVERGENCE_CONTINUATION** (total=592): setup_compat:regime_VOLATILE_UNSUITABLE=486, setup_compat:regime_BREAKOUT_EXPANSION=78, execution:overextended=28
- **FAILED_AUCTION_RECLAIM** (total=6943): setup_compat:regime_STRONG_TREND=3268, execution:overextended=2040, context_floor=1528, setup_compat:regime_VOLATILE_UNSUITABLE=107
- **FUNDING_EXTREME_SIGNAL** (total=1866): execution:trigger_not_confirmed=1866
- **LIQUIDATION_REVERSAL** (total=10): execution:trigger_not_confirmed=10
- **LIQUIDITY_SWEEP_REVERSAL** (total=12541): execution:trigger_not_confirmed=8256, execution:overextended=2704, setup_compat:regime_STRONG_TREND=1581
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_CLEAN_RANGE=4, setup_compat:regime_DIRTY_RANGE=3, execution:overextended=1
- **MEAN_REVERT** (total=8386): setup_compat:regime_STRONG_TREND=4397, setup_compat:regime_WEAK_TREND=3811, execution:overextended=178
- **MOVER_AVWAP_SCALP** (total=2659): execution:overextended=1945, execution:trigger_not_confirmed=714
- **MOVER_TREND_PULLBACK** (total=24327): execution:overextended=12929, execution:trigger_not_confirmed=11398
- **QUIET_COMPRESSION_BREAK** (total=1067): context_floor=899, execution:trigger_not_confirmed=168
- **RANGE_FADE** (total=5876): setup_compat:regime_WEAK_TREND=2923, setup_compat:regime_STRONG_TREND=2324, setup_compat:regime_VOLATILE_UNSUITABLE=326, context_edge=131, execution:overextended=123, setup_compat:regime_BREAKOUT_EXPANSION=27, context_floor=22
- **SR_FLIP_RETEST** (total=18): setup_compat:regime_VOLATILE_UNSUITABLE=18
- **TREND_PULLBACK_EMA** (total=3335): setup_compat:regime_CLEAN_RANGE=2336, setup_compat:regime_DIRTY_RANGE=892, setup_compat:regime_VOLATILE_UNSUITABLE=107

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 248162 | 30.8% |
| RANGING | 220783 | 27.4% |
| TRENDING_UP | 172484 | 21.4% |
| TRENDING_DOWN | 124706 | 15.5% |
| VOLATILE | 39796 | 4.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **472**
- Average confidence gap to threshold: **11.76** (samples=472) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HBARUSDT=42, ETHUSDT=36, ASTERUSDT=35, LTCUSDT=34, 1000PEPEUSDT=29, BTCUSDT=28, DOTUSDT=23, NEARUSDT=19, LINKUSDT=18, TAOUSDT=17

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 431 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 555 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 106 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 92 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 510 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 34 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 208 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 6 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 4 |
| MEAN_REVERT | kept | min_confidence_pass | 8 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 160 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 19 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 420 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1757 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 48 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 10079 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 176 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 25 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 240 |
| RANGE_FADE | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | filtered | min_confidence | 716 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 122 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1895 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 68 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 79.80 | 65.00 | -14.80 | 20.60 | 20.00 | 20.00 | 4.50 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 438 | 56.40 | 63.10 | 6.70 | 19.79 | 19.53 | 17.90 | 1.49 | 11.40 |
| DIVERGENCE_CONTINUATION | kept | 555 | 70.26 | 65.00 | -5.26 | 20.69 | 19.80 | 17.80 | 1.64 | -0.89 |
| FAILED_AUCTION_RECLAIM | filtered | 198 | 52.99 | 62.70 | 9.71 | 20.75 | 18.87 | 20.00 | 3.95 | 11.47 |
| FAILED_AUCTION_RECLAIM | kept | 510 | 70.68 | 65.00 | -5.68 | 21.31 | 19.54 | 20.00 | 4.08 | 0.51 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 56.86 | 65.00 | 8.14 | 19.45 | 19.42 | 17.00 | 1.41 | 13.53 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 34 | 61.92 | 65.00 | 3.08 | 21.40 | 19.11 | 19.13 | 3.35 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 208 | 69.20 | 65.00 | -4.20 | 20.92 | 19.44 | 17.26 | 2.10 | 0.62 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.00 | 65.00 | -3.00 | 21.20 | 19.70 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 10 | 55.68 | 65.00 | 9.32 | 18.41 | 16.40 | 16.12 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 8 | 69.67 | 65.00 | -4.67 | 20.44 | 16.02 | 17.44 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 179 | 55.64 | 65.00 | 9.36 | 21.19 | 18.52 | 15.80 | 3.59 | 3.17 |
| MOVER_AVWAP_SCALP | kept | 420 | 75.90 | 65.00 | -10.90 | 20.06 | 18.12 | 15.80 | 4.89 | 1.54 |
| MOVER_TREND_PULLBACK | filtered | 1805 | 52.40 | 63.40 | 11.00 | 20.13 | 18.68 | 15.80 | 4.49 | 15.45 |
| MOVER_TREND_PULLBACK | kept | 10079 | 77.00 | 65.00 | -12.00 | 19.91 | 18.63 | 15.80 | 4.52 | 0.78 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 77.70 | 65.00 | -12.70 | 20.90 | 19.20 | 15.70 | 4.50 | 10.80 |
| QUIET_COMPRESSION_BREAK | filtered | 201 | 51.45 | 65.00 | 13.55 | 21.52 | 19.65 | 20.00 | 0.00 | 9.45 |
| QUIET_COMPRESSION_BREAK | kept | 240 | 74.71 | 65.00 | -9.71 | 20.52 | 19.79 | 20.00 | 0.00 | 0.05 |
| RANGE_FADE | filtered | 4 | 52.70 | 65.00 | 12.30 | 24.00 | 18.10 | 17.70 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 838 | 56.95 | 64.32 | 7.37 | 20.76 | 19.85 | 15.76 | 1.42 | 10.82 |
| SR_FLIP_RETEST | kept | 1895 | 71.06 | 65.00 | -6.06 | 20.56 | 19.92 | 15.75 | 2.10 | 0.45 |
| TREND_PULLBACK_EMA | kept | 68 | 81.62 | 65.00 | -16.62 | 20.00 | 20.00 | 17.53 | 5.67 | -2.65 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 79.80 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 9.30 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 438 | 56.40 | 23.05 | 14.23 | 4.63 | 11.74 | 5.34 | 8.92 | 1.49 |
| DIVERGENCE_CONTINUATION | kept | 555 | 70.26 | 21.35 | 16.92 | 4.97 | 11.90 | 5.75 | 9.06 | 1.64 |
| FAILED_AUCTION_RECLAIM | filtered | 198 | 52.99 | 20.60 | 16.14 | 6.32 | 11.43 | 6.29 | 5.34 | 3.95 |
| FAILED_AUCTION_RECLAIM | kept | 510 | 70.68 | 23.21 | 14.51 | 4.89 | 11.81 | 6.11 | 6.62 | 4.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 56.86 | 20.29 | 13.88 | 3.00 | 16.12 | 10.00 | 7.45 | 1.41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 34 | 61.92 | 21.00 | 14.00 | 6.00 | 12.18 | 6.00 | 7.39 | 3.35 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 208 | 69.20 | 24.56 | 14.02 | 3.89 | 13.59 | 6.50 | 5.16 | 2.10 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.00 | 25.00 | 14.00 | 3.00 | 11.00 | 5.00 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 10 | 55.68 | 25.00 | 15.60 | 8.40 | 12.00 | 7.40 | 2.28 | 0.00 |
| MEAN_REVERT | kept | 8 | 69.67 | 23.00 | 17.00 | 4.12 | 12.00 | 8.19 | 5.36 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 179 | 55.64 | 18.56 | 18.00 | 8.19 | 12.84 | 4.94 | 5.25 | 3.59 |
| MOVER_AVWAP_SCALP | kept | 420 | 75.90 | 18.51 | 18.00 | 7.93 | 13.47 | 5.47 | 9.24 | 4.89 |
| MOVER_TREND_PULLBACK | filtered | 1805 | 52.40 | 18.72 | 18.01 | 8.01 | 13.27 | 5.51 | 8.60 | 4.49 |
| MOVER_TREND_PULLBACK | kept | 10079 | 77.00 | 19.30 | 18.00 | 8.03 | 13.03 | 5.77 | 9.18 | 4.52 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 77.70 | 17.00 | 18.00 | 15.00 | 14.00 | 10.00 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 201 | 51.45 | 18.03 | 17.50 | 11.57 | 14.37 | 6.22 | 3.88 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 240 | 74.71 | 18.97 | 17.08 | 11.86 | 13.99 | 6.72 | 6.88 | 0.00 |
| RANGE_FADE | filtered | 4 | 52.70 | 25.00 | 18.00 | 3.00 | 12.00 | 5.00 | 4.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 838 | 56.95 | 18.65 | 16.54 | 4.73 | 12.48 | 6.42 | 7.53 | 1.42 |
| SR_FLIP_RETEST | kept | 1895 | 71.06 | 22.23 | 16.47 | 4.51 | 13.34 | 6.23 | 7.85 | 2.10 |
| TREND_PULLBACK_EMA | kept | 68 | 81.62 | 17.71 | 18.00 | 8.16 | 14.00 | 8.29 | 9.97 | 5.67 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 79.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 438 | 56.40 | 0.00 | 0.00 | 2.09 | 0.00 | 1.29 | 0.00 | 0.00 | 0.00 | **3.38** |
| DIVERGENCE_CONTINUATION | kept | 555 | 70.26 | 0.00 | 0.00 | 0.25 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **0.34** |
| FAILED_AUCTION_RECLAIM | filtered | 198 | 52.99 | 0.00 | 0.00 | 0.62 | 0.00 | 7.18 | 0.00 | 0.00 | 0.00 | **7.80** |
| FAILED_AUCTION_RECLAIM | kept | 510 | 70.68 | 0.00 | 0.00 | 0.17 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.18** |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 56.86 | 0.00 | 0.00 | 7.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.06** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 34 | 61.92 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 208 | 69.20 | 0.00 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.62** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 10 | 55.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 8 | 69.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 179 | 55.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.12 | **2.12** |
| MOVER_AVWAP_SCALP | kept | 420 | 75.90 | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | **0.33** |
| MOVER_TREND_PULLBACK | filtered | 1805 | 52.40 | 0.83 | 0.00 | 1.24 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | **2.67** |
| MOVER_TREND_PULLBACK | kept | 10079 | 77.00 | 0.06 | 0.00 | 0.30 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.48** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 77.70 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 201 | 51.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 6.17 | **6.56** |
| QUIET_COMPRESSION_BREAK | kept | 240 | 74.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.88 | 0.00 | 0.00 | 0.00 | **0.88** |
| RANGE_FADE | filtered | 4 | 52.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 838 | 56.95 | 0.00 | 0.00 | 0.50 | 0.00 | 1.44 | 0.00 | 0.00 | 0.27 | **2.21** |
| SR_FLIP_RETEST | kept | 1895 | 71.06 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | **0.30** |
| TREND_PULLBACK_EMA | kept | 68 | 81.62 | 0.00 | 0.00 | 0.07 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.18** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=676 (14.9%) | WOULD_LOSE=1087 | WOULD_EXPIRE=2776 | pending (awaiting window)=461

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 39 | 0.0% | 13.1 | 0.0 | +0.34 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 712 | 0.0% | 228.4 | 0.0 | +0.32 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 457 | 0.0% | 137.4 | 0.0 | +0.30 | **KEEP** |
| dispatch_cooldown | 188 | 1.6% | 66.7 | 3.4 | +0.34 | **KEEP** |
| dispatch_staleness_v2 | 236 | 55.1% | 74.8 | 108.4 | -0.14 | **TUNE** |
| level_still_in_play | 1331 | 24.3% | 226.8 | 176.4 | +0.04 | **TUNE** |
| min_confidence | 1237 | 13.7% | 661.7 | 247.4 | +0.33 | **KEEP** |
| quiet_scalp_block | 137 | 8.8% | 52.9 | 13.1 | +0.29 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 6 | 33.3% | 1.2 | 1.3 | -0.02 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 44 | 20.5% | 36.6 | 6.3 | +0.69 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 71 | 28.2% | 45.3 | 24.2 | +0.30 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 81 | 9.9% | 62.4 | 18.0 | +0.55 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 91696 across 20 strategies; 2071 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 21620 | 114/21506/0 | 58% | +0.09 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.27R) |
| FAILED_AUCTION_RECLAIM | 14969 | 28/14941/0 | 55% | +0.07 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 14598 | 2/14596/0 | 42% | -0.25 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.30R) |
| DIVERGENCE_CONTINUATION | 8698 | 7/8691/0 | 44% | -0.14 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.45R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 6599 | 0/6599/0 | 46% | -0.11 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 3564 | 0/0/3564 | 40% | -0.03 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.03R) |
| LIQUIDITY_SWEEP_REVERSAL | 3373 | 9/3364/0 | 44% | -0.14 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| SHADOW_RANGE_FADE | 3343 | 0/0/3343 | 42% | +0.23 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.25R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.96R) |
| MEAN_REVERT | 3107 | 0/3107/0 | 80% | +0.58 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_FUNDING_FADE | 2738 | 0/0/2738 | 40% | -0.30 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.31R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.94R) |
| MOVER_AVWAP_SCALP | 2293 | 29/2264/0 | 36% | -0.29 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | LONDON/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.20R) |
| RANGE_FADE | 2024 | 0/2024/0 | 7% | -0.96 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.34R) |
| TREND_PULLBACK_EMA | 1623 | 2/1621/0 | 51% | -0.15 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.12R) |
| VOLUME_SURGE_BREAKOUT | 1588 | 12/1576/0 | 38% | -0.13 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.19R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 436 | 2/434/0 | 35% | -0.14 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 277 | 0/0/277 | 45% | -0.23 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.80R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 6 | 1/5/0 | 50% | -0.24 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 44 | 48% / -0.22R | 44 | 52% / -0.03R | +0.18 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| MEAN_REVERT | 265 | 59% / +0.15R | 265 | 55% / +0.24R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 2239 | 45% / -0.19R | 2239 | 48% / -0.10R | +0.09 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 472 | 51% / -0.15R | 472 | 55% / -0.07R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 539 | 45% / -0.13R | 539 | 51% / -0.05R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 47 | 40% / -0.04R | 47 | 43% / -0.11R | -0.07 | **FIXED** |
| MOVER_AVWAP_SCALP | 173 | 41% / -0.13R | 173 | 44% / -0.06R | +0.07 | **ATR** |
| RANGE_FADE | 156 | 6% / -0.99R | 156 | 8% / -0.94R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 942 | 44% / -0.12R | 942 | 44% / -0.14R | -0.02 | **FIXED** |
| MOVER_TREND_PULLBACK | 2462 | 56% / +0.02R | 2462 | 58% / +0.04R | +0.02 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1887 | 47% / -0.09R | 1887 | 47% / -0.08R | +0.02 | **ATR** |
| BREAKDOWN_SHORT | 12 | 25% / -0.32R | 12 | 25% / -0.29R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 8 | 12% / -0.76R | 8 | 38% / -0.32R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 5 | 60% / +0.03R | 5 | 60% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 2222 | 30% | -0.12R | 215 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 163 | 43% | -0.09R | 71 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 12 | 42% | -0.04R | 11 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 767 | 28% / -2.53R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 4 | 25% / -1.11R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 1170 | 39% / -0.59R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 570 | 35% / -0.80R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 18 | 17% / -2.06R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 290 | 26% / -3.60R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 235 | 38% / +0.18R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 136 | 43% / -2.35R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 10 | 10% / -8.51R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 27 | 26% / -2.98R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 83 | 34% / -0.23R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 4 | 0% / -0.92R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 13 | 46% / -0.02R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 7 | 29% / -0.53R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 3 | 0% / -1.11R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| FAILED_AUCTION_RECLAIM | min_confidence | 26 | 80.8% | -1.40 | **DROP** |
| LIQUIDITY_SWEEP_REVERSAL | min_confidence | 21 | 81.0% | -1.29 | **DROP** |
| MEAN_REVERT | dispatch_staleness_v2 | 1 | 100.0% | -1.25 | **INSUFFICIENT_SAMPLE** |
| FUNDING_EXTREME_SIGNAL | min_confidence | 7 | 71.4% | -0.65 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 188 | 66.0% | -0.36 | **DROP** |
| MOVER_TREND_PULLBACK | level_still_in_play | 931 | 28.9% | -0.03 | **TUNE** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 6 | 33.3% | -0.02 | **INSUFFICIENT_SAMPLE** |
| MOVER_AVWAP_SCALP | min_confidence | 102 | 4.9% | +0.01 | **TUNE** |
| QUIET_COMPRESSION_BREAK | min_confidence | 7 | 0.0% | +0.06 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 20 | 0.0% | +0.06 | **TUNE** |
| MOVER_AVWAP_SCALP | quiet_scalp_block | 4 | 0.0% | +0.10 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | level_still_in_play | 95 | 0.0% | +0.15 | **KEEP** |
| MOVER_TREND_PULLBACK | quiet_scalp_block | 5 | 0.0% | +0.16 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | level_still_in_play | 241 | 22.4% | +0.16 | **KEEP** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 28 | 0.0% | +0.17 | **KEEP** |
| DIVERGENCE_CONTINUATION | quiet_scalp_block | 7 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 19 | 26.3% | +0.20 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 40 | 0.0% | +0.26 | **KEEP** |
| QUIET_COMPRESSION_BREAK | quiet_scalp_block | 34 | 0.0% | +0.26 | **KEEP** |
| SR_FLIP_RETEST | min_confidence | 295 | 22.0% | +0.26 | **KEEP** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 71 | 28.2% | +0.30 | **KEEP** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 457 | 0.0% | +0.30 | **KEEP** |
| FAILED_AUCTION_RECLAIM | context_floor:FAILED_AUCTION_RECLAIM | 712 | 0.0% | +0.32 | **KEEP** |
| RANGE_FADE | context_edge:RANGE_FADE | 39 | 0.0% | +0.34 | **KEEP** |
| MOVER_TREND_PULLBACK | dispatch_cooldown | 188 | 1.6% | +0.34 | **KEEP** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 29 · alerting: **6** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 357/357 unfetchable (100%); top cause: 15m history rolled off before the stamp; symbols: 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ADAUSDT, AKEUSDT +45 more (streak 174/6) (sustained 174 cycles)
- **ALERT** `sar_resolution_progress` — 0 verdicts produced while 999 records await one (0 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 13/12) (sustained 13 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 174/6) (sustained 174 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 3959x (gate reads 0x, withheld 0x — refusal dark); last GIGGLEUSDT age=37184.3s (streak 107/6) (sustained 107 cycles)
- **ALERT** `mean_revert_emission` — 569 detections since last emission (emitted_total=5) — and the blocked candidates measure +0.58R over n=3107, so the gating is COSTING us. Check gate rejections. (streak 15/6) (sustained 15 cycles)
- **ALERT** `auto_dispatch` — 15 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=15) (streak 105/3) (sustained 105 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 15 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=15) (streak 105/3) | 105 |
| btc_reference | ok | BTC ref 64344.00 | 0 |
| candle_coverage | ok | 88/98 symbols with ≥20 15m candles, 81/98 updated within 45m | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 174/6) | 174 |
| context_emission_policy | ok | output +36 / upstream +40 | 0 |
| edge_reconciliation | ok | max divergence MOVER_AVWAP_SCALP +0.25R (< 0.3) | 0 |
| emission_controller | ok | last cycle 1630s ago; live_overrides=21 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=10 wasted_promotions=0 pruned=0 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +6 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 569 detections since last emission (emitted_total=5) — and the blocked candidates measure +0.58R over n=3107, so the gating is COSTING us. Check gate rejections. (streak 15/6) | 15 |
| mean_revert_path | ok | output +0 / upstream +6 | 0 |
| mover_admission_metadata | ok | 850 symbols known, 150 marked TRADIFI_PERPETUAL | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.96R over n=2024 — emitting them would lose money | 0 |
| range_fade_path | ok | output +14 / upstream +6 | 0 |
| sar_alignment_crosscheck | ok | 14/655 disagreed (2.1%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +6 | 0 |
| sar_ledger_candles | violating | 357/357 unfetchable (100%); top cause: 15m history rolled off before the stamp; symbols: 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ADAUSDT, AKEUSDT +45 more (streak 174/6) | 174 |
| sar_live_arms | ok | 3 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 999 records await one (0 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 13/12) | 13 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 3959x (gate reads 0x, withheld 0x — refusal dark); last GIGGLEUSDT age=37184.3s (streak 107/6) | 107 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +5 / upstream +6 | 0 |
| suppression_audit | ok | output +6 / upstream +40 | 0 |
| tuned_variants | ok | seen=2725 stamped=328 skipped=2397 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3908273`
- `Path funnel` emissions: `100`
- `Regime distribution` emissions: `100`
- `QUIET_SCALP_BLOCK` events: `472`
- `confidence_gate` events: `17710`
- `free_channel_post` events: `22`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **5**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 7 | 2616 | 3247 | 5579 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 5 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **22**

| Source | Count |
|---|---:|
| signal_close | 16 |
| regime_shift | 6 |

- By severity: HIGH=22

## Dependency readiness
- cvd: presence[present=618804] state[populated=618804] buckets[many=618725, some=79] sources[none] quality[none]
- funding_rate: presence[absent=56863, present=561941] state[empty=56863, populated=561941] buckets[few=561941, none=56863] sources[none] quality[none]
- liquidation_clusters: presence[absent=370730, present=248074] state[empty=370730, populated=248074] buckets[few=203459, none=370730, some=44615] sources[none] quality[none]
- oi_snapshot: presence[absent=54094, present=564710] state[empty=54094, populated=564710] buckets[many=564710, none=54094] sources[none] quality[none]
- order_book: presence[absent=165527, present=453277] state[populated=453277, unavailable=165527] buckets[few=453277, none=165527] sources[book_ticker=453277, unavailable=165527] quality[none=165527, top_of_book_only=453277]
- orderblocks: presence[absent=618804] state[empty=618804] buckets[none=618804] sources[not_implemented=618804] quality[none]
- recent_ticks: presence[present=618804] state[populated=618804] buckets[many=618804] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.503041386604309` sec
- Median create→first breach: `3559.27924656868` sec
- Median create→terminal: `3827.8321145772934` sec
- Median first breach→terminal: `2.1262409687042236` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.7687 | 657.1661288738251 | 657.5015358924866 |
| MOVER_TREND_PULLBACK | 15 | 15 | 0.0 | 60.0 | 0.0 | 0.0 | 0.9941 | 3580.531746149063 | 4066.72323012352 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 21588 | 108 | 11686 | 0.0 | 0.0 | None | None | 9902 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3887 | 1 | 3790 | 0.0 | 0.0 | None | None | 97 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-122`
- Gating Δ: `38457`
- No-generation Δ: `314626`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.7007, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.7007, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.498, "current_avg_pnl": 0.9941, "current_win_rate": 0.0, "previous_avg_pnl": -0.5039, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -81, "geometry_changed_delta": 0, "geometry_preserved_delta": -1482, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -154, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
