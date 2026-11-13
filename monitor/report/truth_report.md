# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `383` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 131 | 131 | 131 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 13203 | 13203 | 11075 | 28 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 70931 | 70932 | 32 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 71673 | 71674 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 71125 | 68053 | 3595 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 71697 | 71009 | 778 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 71565 | 71363 | 229 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 60866 | 60884 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 71791 | 71834 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 71845 | 68826 | 4508 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 75337 | 81338 | 768 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 70969 | 65997 | 9281 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 71174 | 71174 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 71679 | 71693 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 71075 | 70929 | 190 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 73344 | 71729 | 2035 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 70659 | 70961 | 80 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 60160 | 56328 | 4254 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 60587 | 60219 | 489 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 70891 | 70906 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 60891 | 60903 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3148 | 3148 | 2702 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 585 | 585 | 173 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20112 | 20112 | 19909 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 3 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11741 | 11741 | 9785 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1838 | 1838 | 247 | 65 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 25099 | 25099 | 11081 | 360 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1001 | 1001 | 333 | 56 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4577 | 4577 | 3441 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 352 | 352 | 74 | 12 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2182 | 2182 | 1691 | 29 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 58 | 58 | 22 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=70932): breakout_not_found=38193, basic_filters_failed=19764, move_not_fresh=9564, breakout_stale=2498, retest_proximity_failed=705, volume_spike_missing=193, move_exhausted=9, missing_fvg_or_orderblock=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=71675): cls_disabled_merged_into_lsr=71675
- **EVAL::DIVERGENCE_CONTINUATION** (total=68054): cvd_divergence_failed=27993, basic_filters_failed=16532, h1_trend_not_aligned=14755, ema_alignment_reject=7605, retest_proximity_failed=710, missing_fvg_or_orderblock=459
- **EVAL::FAILED_AUCTION_RECLAIM** (total=71010): auction_not_detected=47022, basic_filters_failed=16172, reclaim_hold_failed=3366, tail_too_small=2436, regime_blocked=1993, rsi_reject=21
- **EVAL::FUNDING_EXTREME** (total=71364): funding_not_extreme=51492, basic_filters_failed=16295, ema_alignment_reject=1724, rsi_reject=817, missing_funding_rate=615, momentum_reject=199, cvd_divergence_failed=178, missing_fvg_or_orderblock=44
- **EVAL::LIQUIDATION_REVERSAL** (total=60884): cascade_threshold_not_met=43941, basic_filters_failed=16371, rsi_reject=280, cvd_divergence_failed=264, missing_fvg_or_orderblock=28
- **EVAL::MA_CROSS_TREND_SHIFT** (total=71835): no_ma_cross=54082, basic_filters_failed=16551, ma_cross_cooldown=724, ma_cross_htf_misaligned=478
- **EVAL::MEAN_REVERT** (total=68827): no_extension=61426, basic_filters_failed=7401
- **EVAL::MOVER_AVWAP_SCALP** (total=81339): no_avwap_tag=33352, basic_filters_failed=19986, no_mover_leg=19580, avwap_slope_against=4922, avwap_reclaim_no_volume=1900, no_avwap_reclaim=1536, anchor_too_recent=63
- **EVAL::MOVER_TREND_PULLBACK** (total=65997): mover_run_too_small=32547, basic_filters_failed=19882, no_reclaim=12019, no_pullback_tag=1549
- **EVAL::OPENING_RANGE_BREAKOUT** (total=71175): feature_disabled=71175
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=71694): regime_blocked=55110, breakout_not_found=11043, basic_filters_failed=3470, adx_reject=2016, ema_alignment_reject=55
- **EVAL::QUIET_COMPRESSION_BREAK** (total=70930): compression_not_detected=33239, regime_blocked=18507, basic_filters_failed=12692, breakout_not_detected=5887, volume_confirmation_failed=590, rsi_reject=12, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=71730): no_range_edge=64323, basic_filters_failed=7407
- **EVAL::SR_FLIP_RETEST** (total=70962): flip_close_not_confirmed=46441, basic_filters_failed=16154, retest_out_of_zone=1988, regime_blocked=1975, h1_break_not_confirmed=1832, long_break_volume_thin=1553, reclaim_hold_failed=646, ema_alignment_reject=128, whipsaw_flip=100, wick_quality_failed=79, long_acceptance_not_held=47, missing_fvg_or_orderblock=19
- **EVAL::STANDARD** (total=56328): momentum_reject=18133, adx_reject=15896, macd_reject=7262, sweeps_not_detected=6107, basic_filters_failed=5497, ema_alignment_reject=2463, htf_poi_unanchored=681, invalid_sl_geometry=226, rsi_reject=62, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=60219): h1_trend_not_aligned=17348, ema_alignment_reject=12411, basic_filters_failed=9982, h1_pullback_not_confirmed=6958, ema_not_tested_prev=4574, no_ema_reclaim_close=4045, body_conviction_fail=1838, rsi_reject=1387, prev_already_below_emas=779, no_prev_low_break=428, momentum_flat=193, prev_already_above_emas=129, no_prev_high_break=63, ema21_not_tagged=41, missing_fvg_or_orderblock=28, momentum_reject=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=70906): breakout_not_found=40061, basic_filters_failed=19761, move_not_fresh=6988, breakout_stale=2951, retest_proximity_failed=960, volume_spike_missing=179, move_exhausted=3, missing_fvg_or_orderblock=3
- **EVAL::WHALE_MOMENTUM** (total=60903): momentum_reject=43846, recent_ticks_insufficient=12742, basic_filters_failed=4315

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=210): setup_compat:regime_VOLATILE_UNSUITABLE=193, setup_compat:regime_BREAKOUT_EXPANSION=17
- **FAILED_AUCTION_RECLAIM** (total=698): execution:overextended=308, setup_compat:regime_STRONG_TREND=264, context_floor=114, setup_compat:regime_VOLATILE_UNSUITABLE=12
- **FUNDING_EXTREME_SIGNAL** (total=397): execution:trigger_not_confirmed=397
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=4858): execution:trigger_not_confirmed=2067, execution:overextended=1603, setup_compat:regime_STRONG_TREND=1188
- **MA_CROSS_TREND_SHIFT** (total=11): setup_compat:regime_CLEAN_RANGE=4, execution:trigger_not_confirmed=3, setup_compat:regime_DIRTY_RANGE=3, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=3361): setup_compat:regime_STRONG_TREND=1699, setup_compat:regime_WEAK_TREND=1110, execution:overextended=549, entry_quality=3
- **MOVER_AVWAP_SCALP** (total=1157): execution:overextended=724, entry_quality=254, execution:trigger_not_confirmed=179
- **MOVER_TREND_PULLBACK** (total=12132): execution:trigger_not_confirmed=6874, execution:overextended=3227, entry_quality=2031
- **QUIET_COMPRESSION_BREAK** (total=10): execution:trigger_not_confirmed=10
- **RANGE_FADE** (total=2322): setup_compat:regime_STRONG_TREND=1032, setup_compat:regime_WEAK_TREND=653, setup_compat:regime_VOLATILE_UNSUITABLE=251, execution:overextended=250, context_edge=122, setup_compat:regime_BREAKOUT_EXPANSION=14
- **TREND_PULLBACK_EMA** (total=2164): setup_compat:regime_CLEAN_RANGE=1144, setup_compat:regime_DIRTY_RANGE=806, entry_quality=139, setup_compat:regime_VOLATILE_UNSUITABLE=75
- **VOLUME_SURGE_BREAKOUT** (total=16): execution:overextended=16

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 210051 | 52.0% |
| QUIET | 78602 | 19.4% |
| TRENDING_DOWN | 60848 | 15.1% |
| TRENDING_UP | 37892 | 9.4% |
| VOLATILE | 16873 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **324**
- Average confidence gap to threshold: **15.69** (samples=324) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ARBUSDT=55, BNBUSDT=28, AAVEUSDT=27, OPUSDT=26, FILUSDT=26, XMRUSDT=24, ENAUSDT=18, BTCUSDT=14, LINKUSDT=12, SOLUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 153 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 10 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 229 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 54 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 33 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 36 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 91 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 12 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 97 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 4 |
| MEAN_REVERT | kept | min_confidence_pass | 21 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 386 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 703 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2110 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 155 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4628 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 151 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 91 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 271 |
| SR_FLIP_RETEST | filtered | min_confidence | 126 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 65 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 54 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 16 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 185 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 34 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 163 | 58.11 | 64.08 | 5.97 | 20.96 | 19.74 | 17.72 | 2.32 | 11.57 |
| DIVERGENCE_CONTINUATION | kept | 229 | 67.20 | 65.00 | -2.20 | 21.74 | 19.72 | 18.51 | 2.50 | 0.78 |
| FAILED_AUCTION_RECLAIM | filtered | 87 | 53.17 | 63.69 | 10.52 | 19.80 | 19.62 | 20.00 | 2.65 | 2.52 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.20 | 65.00 | 2.80 | 21.20 | 19.90 | 20.00 | 2.50 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 37 | 43.64 | 61.76 | 18.12 | 20.39 | 15.95 | 17.00 | 2.68 | 15.45 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.30 | 65.00 | -4.30 | 20.90 | 14.00 | 17.00 | 7.00 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 1 | 65.30 | 10.00 | -55.30 | 21.20 | 8.00 | 13.90 | 4.00 | 17.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 98 | 54.23 | 64.59 | 10.36 | 22.29 | 17.48 | 17.47 | 0.58 | 1.64 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.17 | 65.00 | -5.17 | 20.66 | 19.11 | 17.76 | 3.75 | -0.25 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 69.27 | 65.00 | -4.27 | 20.43 | 18.23 | 15.80 | 0.00 | 8.67 |
| MEAN_REVERT | filtered | 101 | 46.54 | 64.56 | 18.02 | 19.07 | 16.87 | 13.97 | 0.00 | 18.89 |
| MEAN_REVERT | kept | 21 | 68.06 | 65.00 | -3.06 | 18.60 | 16.48 | 14.53 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 393 | 57.54 | 64.57 | 7.03 | 20.03 | 15.25 | 15.80 | 3.93 | 13.44 |
| MOVER_AVWAP_SCALP | kept | 703 | 80.54 | 65.00 | -15.54 | 20.05 | 16.77 | 15.80 | 4.32 | 3.26 |
| MOVER_TREND_PULLBACK | filtered | 2265 | 53.83 | 64.36 | 10.53 | 20.49 | 18.48 | 15.80 | 4.20 | 20.18 |
| MOVER_TREND_PULLBACK | kept | 4628 | 76.52 | 65.00 | -11.52 | 20.67 | 18.52 | 15.80 | 4.24 | 2.60 |
| QUIET_COMPRESSION_BREAK | filtered | 242 | 48.33 | 64.17 | 15.84 | 21.07 | 19.07 | 20.00 | 0.00 | 14.14 |
| QUIET_COMPRESSION_BREAK | kept | 271 | 76.97 | 65.00 | -11.97 | 20.06 | 19.51 | 20.00 | 0.00 | -0.17 |
| SR_FLIP_RETEST | filtered | 126 | 48.26 | 64.62 | 16.36 | 21.53 | 20.00 | 16.00 | 1.56 | 15.51 |
| SR_FLIP_RETEST | kept | 65 | 73.06 | 65.00 | -8.06 | 20.34 | 20.00 | 15.67 | 2.12 | 0.62 |
| TREND_PULLBACK_EMA | filtered | 70 | 61.71 | 65.00 | 3.29 | 21.22 | 19.67 | 17.77 | 4.97 | 18.85 |
| TREND_PULLBACK_EMA | kept | 185 | 76.66 | 65.00 | -11.66 | 21.16 | 19.91 | 17.63 | 4.64 | 2.21 |
| VOLUME_SURGE_BREAKOUT | filtered | 34 | 41.30 | 62.06 | 20.76 | 18.06 | 16.03 | 20.00 | 3.54 | 17.00 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 68.67 | 65.00 | -3.67 | 17.47 | 18.93 | 20.00 | 5.00 | 7.67 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 163 | 58.11 | 23.13 | 12.29 | 4.95 | 12.63 | 5.96 | 8.39 | 2.32 |
| DIVERGENCE_CONTINUATION | kept | 229 | 67.20 | 23.78 | 13.33 | 3.84 | 11.79 | 5.38 | 8.96 | 2.50 |
| FAILED_AUCTION_RECLAIM | filtered | 87 | 53.17 | 22.26 | 16.48 | 4.03 | 13.36 | 7.55 | 4.35 | 2.65 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.20 | 25.00 | 18.00 | 3.00 | 14.00 | 10.00 | 4.70 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 37 | 43.64 | 21.97 | 13.84 | 6.81 | 13.95 | 8.54 | 3.06 | 2.68 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.30 | 17.00 | 20.00 | 3.00 | 9.00 | 5.00 | 8.30 | 7.00 |
| LIQUIDATION_REVERSAL | filtered | 1 | 65.30 | 25.00 | 20.00 | 15.00 | 8.00 | 5.00 | 5.30 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 98 | 54.23 | 23.61 | 14.73 | 7.01 | 13.96 | 6.33 | 4.64 | 0.58 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.17 | 22.00 | 14.33 | 6.00 | 12.75 | 6.67 | 7.17 | 3.75 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 69.27 | 24.33 | 14.00 | 7.00 | 15.00 | 7.83 | 9.77 | 0.00 |
| MEAN_REVERT | filtered | 101 | 46.54 | 21.34 | 16.46 | 13.90 | 12.61 | 5.00 | 4.74 | 0.00 |
| MEAN_REVERT | kept | 21 | 68.06 | 16.90 | 18.00 | 8.86 | 13.00 | 5.00 | 6.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 393 | 57.54 | 17.64 | 18.01 | 12.08 | 13.32 | 6.79 | 6.75 | 3.93 |
| MOVER_AVWAP_SCALP | kept | 703 | 80.54 | 19.21 | 18.01 | 12.18 | 13.91 | 7.38 | 9.22 | 4.32 |
| MOVER_TREND_PULLBACK | filtered | 2265 | 53.83 | 17.67 | 18.11 | 7.83 | 12.28 | 6.41 | 9.37 | 4.20 |
| MOVER_TREND_PULLBACK | kept | 4628 | 76.52 | 19.52 | 18.03 | 8.29 | 13.07 | 6.59 | 9.47 | 4.24 |
| QUIET_COMPRESSION_BREAK | filtered | 242 | 48.33 | 19.41 | 15.50 | 10.87 | 14.04 | 7.33 | 5.23 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 271 | 76.97 | 19.89 | 16.32 | 12.56 | 14.06 | 6.32 | 9.19 | 0.00 |
| SR_FLIP_RETEST | filtered | 126 | 48.26 | 19.29 | 18.00 | 3.21 | 13.79 | 5.53 | 6.32 | 1.56 |
| SR_FLIP_RETEST | kept | 65 | 73.06 | 22.91 | 14.31 | 5.68 | 13.71 | 5.69 | 9.73 | 2.12 |
| TREND_PULLBACK_EMA | filtered | 70 | 61.71 | 19.41 | 18.00 | 7.50 | 14.34 | 7.26 | 9.07 | 4.97 |
| TREND_PULLBACK_EMA | kept | 185 | 76.66 | 19.49 | 18.00 | 7.90 | 14.24 | 6.20 | 9.69 | 4.64 |
| VOLUME_SURGE_BREAKOUT | filtered | 34 | 41.30 | 19.12 | 15.06 | 13.50 | 12.59 | 5.00 | 4.49 | 3.54 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 68.67 | 22.33 | 16.67 | 13.00 | 13.00 | 5.00 | 6.33 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 163 | 58.11 | 0.00 | 0.00 | 0.84 | 0.00 | 0.52 | 0.04 | 0.00 | 0.00 | **1.40** |
| DIVERGENCE_CONTINUATION | kept | 229 | 67.20 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.14** |
| FAILED_AUCTION_RECLAIM | filtered | 87 | 53.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | **0.50** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 37 | 43.64 | 0.00 | 0.00 | 1.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.30** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 1 | 65.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 98 | 54.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | **0.37** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 69.27 | 0.00 | 0.00 | 1.60 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | **5.60** |
| MEAN_REVERT | filtered | 101 | 46.54 | 0.00 | 0.00 | 0.00 | 0.00 | 7.08 | 0.00 | 0.00 | 1.72 | **8.80** |
| MEAN_REVERT | kept | 21 | 68.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 393 | 57.54 | 0.00 | 0.00 | 1.38 | 0.00 | 3.29 | 0.12 | 0.00 | 1.04 | **5.83** |
| MOVER_AVWAP_SCALP | kept | 703 | 80.54 | 0.00 | 0.00 | 0.91 | 0.00 | 0.53 | 0.27 | 0.00 | 0.18 | **1.89** |
| MOVER_TREND_PULLBACK | filtered | 2265 | 53.83 | 0.62 | 0.00 | 3.60 | 0.00 | 0.85 | 0.14 | 0.00 | 0.01 | **5.22** |
| MOVER_TREND_PULLBACK | kept | 4628 | 76.52 | 0.15 | 0.00 | 0.80 | 0.00 | 0.11 | 0.12 | 0.00 | 0.00 | **1.18** |
| QUIET_COMPRESSION_BREAK | filtered | 242 | 48.33 | 0.00 | 0.00 | 1.65 | 0.00 | 0.54 | 1.02 | 0.00 | 4.71 | **7.92** |
| QUIET_COMPRESSION_BREAK | kept | 271 | 76.97 | 0.00 | 0.00 | 0.06 | 0.00 | 0.15 | 0.45 | 0.00 | 0.00 | **0.66** |
| SR_FLIP_RETEST | filtered | 126 | 48.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.38 | **0.38** |
| SR_FLIP_RETEST | kept | 65 | 73.06 | 0.00 | 0.00 | 0.07 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.18** |
| TREND_PULLBACK_EMA | filtered | 70 | 61.71 | 0.00 | 0.00 | 1.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.65** |
| TREND_PULLBACK_EMA | kept | 185 | 76.66 | 0.00 | 0.00 | 0.18 | 0.00 | 0.54 | 0.00 | 0.00 | 0.00 | **0.72** |
| VOLUME_SURGE_BREAKOUT | filtered | 34 | 41.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.41 | **4.41** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 68.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **187174 held of 838536 seen** across 21 strategies; 4235 cells past the sample floor; **2265 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 48574 | 632/47942/0 | 44% | -0.17 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING/MIDCAP (+1.21R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 24969 | 206/24763/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 14638 | 249/14389/0 | 44% | -0.15 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14112 | 153/13959/0 | 36% | -0.33 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 12791 | 74/12717/0 | 38% | -0.29 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 10443 | 103/10340/0 | 38% | -0.42 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9120 | 431/8689/0 | 45% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8194 | 0/0/8194 | 43% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.23R) | ASIA/RANGE/NORMAL/BTC_FALLING (-1.02R) |
| SHADOW_RANGE_FADE | 7669 | 0/0/7669 | 36% | -0.14 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.25R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_FUNDING_FADE | 7181 | 0/0/7181 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.00R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6506 | 24/6482/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5491 | 69/5422/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4127 | 2/4125/0 | 31% | -0.46 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3919 | 0/3919/0 | 28% | -0.42 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 2552 | 6/2546/0 | 47% | +0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1710 | 0/0/1710 | 52% | -0.08 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.60R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 534 | 0/534/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 212 | 34/178/0 | 43% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 377 | 27% / -0.57R | 377 | 53% / -0.09R | +0.49 | **ATR** |
| TREND_PULLBACK_EMA | 1259 | 38% / -0.37R | 1259 | 50% / -0.08R | +0.29 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1581 | 42% / -0.37R | 1581 | 57% / -0.12R | +0.25 | **ATR** |
| MA_CROSS_TREND_SHIFT | 65 | 43% / -0.19R | 65 | 48% / -0.05R | +0.14 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 220 | 37% / -0.19R | 220 | 48% / -0.05R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 660 | 46% / -0.27R | 660 | 50% / -0.15R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8967 | 48% / -0.14R | 8967 | 53% / -0.02R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 2660 | 45% / -0.16R | 2660 | 51% / -0.05R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1532 | 41% / -0.23R | 1532 | 44% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1851 | 48% / -0.12R | 1851 | 53% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 138 | 41% / +0.03R | 138 | 47% / +0.08R | +0.05 | **ATR** |
| MEAN_REVERT | 449 | 47% / -0.16R | 449 | 45% / -0.17R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1597 | 47% / -0.12R | 1597 | 47% / -0.12R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11944 | 28% | -0.25R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2660 | 49% | -0.05R | 239 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 141 | 50% | -0.05R | 70 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1636 | 33% / -0.20R | +0.86 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1848 | 39% / -0.15R | +0.86 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3219 | 35% / -0.20R | +0.64 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10927 | 36% / -0.19R | +0.34 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2159 | 36% / -0.15R | +0.13 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1550 | 36% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1271 | 32% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 322 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 486 | 31% / -0.23R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 372 | 48% / -0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 96 | 44% / -0.00R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 581 | 35% / -0.28R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 102 | 28% / -0.36R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 43 | 44% / -0.22R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=125, profile_reject=5. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) (sustained 6 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 140/6) (sustained 140 cycles)
- **ALERT** `range_fade_emission` — 1686 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=2546, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 30/6) (sustained 30 cycles)
- **ALERT** `tuned_variants` — 211 non-stamps — atr_arm_uncomputable=211 (seen=4478 stamped=517 skipped=3750) (streak 137/6) (sustained 137 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 30742620 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 22 arms current, none stalled; covering 2049/2049 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 42 arms current, none stalled; covering 1050/1050 signals (100%) | 0 |
| auto_dispatch | ok | 27 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=28. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 297/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 68983.10 | 0 |
| candle_coverage | ok | 96/96 symbols with ≥20 15m candles, 96/96 updated within 45m [fresh=96; 74 Tier-1 futures + 22 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 763 dup bars, 0 undedupable; ws 0 out-of-order, 250 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +35 / upstream +20 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1694/1713 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 145 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1682/1701 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 7419213 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 140/6) | 140 |
| emission_controller | ok | last cycle 1583s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=529, MOVER_AVWAP_SCALP=472, MOVER_TREND_PULLBACK=4234, RANGE_FADE=607, TREND_PULLBACK_EMA=158), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=125, profile_reject=5. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) | 6 |
| firestore_read_budget | ok | 1,312 reads/day of 50,000 [engine 1,291, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1964 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +7 / upstream +281 | 0 |
| indicator_cache_key | ok | 37173 frozen value(s) avoided; 106131 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=5422 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +4 / upstream +281 | 0 |
| mover_admission_metadata | ok | 946 symbols known, 237 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 22 held, 22 with scan counts, 22 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2153 rows held, 3525059 evicted (sampled: execution:trigger_not_confirmed 291/1242857, execution:overextended 291/1096610, setup_compat:regime_STRONG_TREND 291/602020) | 0 |
| price_action_lane | ok | 349064 evaluated, 503 emitted; layer1 503 stamped / 0 blind; cooldown=57590, delta_opposed=32392, no_footprint=129113, no_opposing_target=336, no_sweep=99501, rr_below_floor=29629 | 0 |
| promoted_pair_integrity | ok | 22/22 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 1686 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=2546, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 30/6) | 30 |
| range_fade_path | ok | output +5 / upstream +281 | 0 |
| sar_alignment_crosscheck | ok | 319/9935 disagreed (3.2%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +281 | 0 |
| sar_hold_arm | ok | 1876 held arms settled, 124 unscored, 42 still walking (35 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 10/43 unfetchable (23%); top cause: gap or duplicate bar in the 15m window; symbols: BNBUSDT, ONEUSDT, PONSUSDT, ZROUSDT | 0 |
| sar_live_arms | ok | 42 arms current, none stalled; covering 1049/1049 signals (100%) | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 443 records await one (33 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 68.54s, worst 181.82s over 4269 lifetime cycles; lifetime 126 over 60s, 8 over 120s (plus 1/0 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.07s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 154415 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (0.46s to run, worst 132.98s), 413 overrun(s) of 3136 cycles, TTL 900s; slowest signals=0.15s, data_intake=0.05s, pair_context=0.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +104 / upstream +281 | 0 |
| structural_snap | ok | 5999/5999 measured, 27 blind, 0 levels moved (refusals: redetect_cooldown=474) | 0 |
| structural_veto_lane | ok | 893 stamped; 0 with no readable level book, 18 with clear air ahead, 733 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +281 / upstream +20 | 0 |
| tuned_variants | violating | 211 non-stamps — atr_arm_uncomputable=211 (seen=4478 stamped=517 skipped=3750) (streak 137/6) | 137 |
| unlock_shorts | ok | 18 open, 43 scheduled, calendar 13.9h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 8 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2061590`
- `Path funnel` emissions: `50`
- `Regime distribution` emissions: `50`
- `QUIET_SCALP_BLOCK` events: `324`
- `confidence_gate` events: `9739`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **87**
- Total REST-fallback activations: **8**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 8 | 12105 | 42121 | 77412 | 0 |
| futures_aggtrade | 52 | 10817 | 44854 | 68993 | 0 |
| futures_depth | 3 | 25182 | 25182 | 32797 | 0 |
| futures_liq | 5 | 3909 | 8265 | 12998 | 0 |
| futures_mover | 19 | 15783 | 52465 | 60123 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 8 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=307628] state[populated=307628] buckets[many=307340, some=288] sources[none] quality[none]
- funding_rate: presence[absent=23547, present=284081] state[empty=23547, populated=284081] buckets[few=284081, none=23547] sources[none] quality[none]
- liquidation_clusters: presence[absent=162641, present=144987] state[empty=162641, populated=144987] buckets[few=114125, none=162641, some=30862] sources[none] quality[none]
- oi_snapshot: presence[absent=22928, present=284700] state[empty=22928, populated=284700] buckets[few=95, many=284014, none=22928, some=591] sources[none] quality[none]
- order_book: presence[absent=92754, present=214874] state[populated=214874, unavailable=92754] buckets[few=214874, none=92754] sources[book_ticker=214874, unavailable=92754] quality[none=92754, top_of_book_only=214874]
- orderblocks: presence[absent=307628] state[empty=307628] buckets[none=307628] sources[measured_dark=307628] quality[none]
- recent_ticks: presence[present=307628] state[populated=307628] buckets[many=307628] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.8957390785217285` sec
- Median create→first breach: `3829.0660985708237` sec
- Median create→terminal: `3829.066250562668` sec
- Median first breach→terminal: `0.0001704692840576172` sec
- Fast-failure buckets: `{"under_120s": {"count": 3, "pct": 6.8}, "under_180s": {"count": 3, "pct": 6.8}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 3, "pct": 6.8}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 14 | 14 | 0.8000000000000097 | 1.3700904150433053 | 0.7822164194818961 | 0 | 13 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 11.355914141032414 | 2.3138973841735377 | 4.907699977839961 | 1 | 0 |
| MEAN_REVERT | 1 | 1 | 1.7203190927088767 | 1.6986431605944639 | 1.0127607331647144 | 1 | 0 |
| MOVER_AVWAP_SCALP | 1 | 1 | 4.763949969702834 | 3.0 | 1.587983323234278 | 1 | 0 |
| MOVER_TREND_PULLBACK | 15 | 15 | 4.192230230607755 | 3.0 | 1.493048348926483 | 14 | 1 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 1.2678154648153823 | 1.5337532551816404 | 0.882157647128262 | 0 | 8 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.7285165243280622 | 2.0895984578155105 | 0.7806386190955287 | 0 | 2 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 14 | 1.8393462103256406 | 1.6587905601989141 | 2 | 0 | 0 | 4 | 2 | 8 |
| MA_CROSS_TREND_SHIFT | 1 | 17.033871211548636 | 3.1232224809916262 | 0 | 0 | 0 | 1 | 0 | 0 |
| MEAN_REVERT | 1 | 2.612090048284944 | 2.6779147175017304 | 1 | 0 | 0 | 0 | 0 | 0 |
| MOVER_AVWAP_SCALP | 1 | 7.538329322791338 | 6.502578205568918 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_TREND_PULLBACK | 15 | 6.559785559799369 | 4.973917869034401 | 2 | 0 | 0 | 13 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 10 | 3.6356232799390975 | 2.3429994197863064 | 0 | 0 | 0 | 7 | 2 | 3 |
| TREND_PULLBACK_EMA | 2 | 2.922071122482581 | 2.8151561371402796 | 0 | 0 | 0 | 1 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 14 | 14 | 35.7 | 28.6 | 35.7 | 0.0 | 0.3059 | 2744.688694000244 | 2745.0108880996704 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.1232 | 2312.6962110996246 | 2313.610470056534 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.6779 | 2536.2402839660645 | 2537.1139421463013 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -4.7638 | 311.23400688171387 | 311.2340478897095 |
| MOVER_TREND_PULLBACK | 15 | 15 | 33.3 | 40.0 | 33.3 | 0.0 | 0.455 | 3695.691905975342 | 3696.6750741004944 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 40.0 | 40.0 | 40.0 | 0.0 | 0.7343 | 11750.717588543892 | 11754.834110975266 |
| TREND_PULLBACK_EMA | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.9969 | 2265.875135540962 | 2266.1703593730927 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 352 | 12 | 74 | 0.0 | 0.0 | None | None | 278 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2182 | 29 | 1691 | 50.0 | 0.0 | 2265.875135540962 | 2266.1703593730927 | 491 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `48`
- Gating Δ: `21670`
- No-generation Δ: `399993`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.3072, "current_avg_pnl": 0.3059, "current_win_rate": 35.7, "previous_avg_pnl": -1.0013, "previous_win_rate": 0.0, "win_rate_delta": 35.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -4.698, "current_avg_pnl": -4.7638, "current_win_rate": 0.0, "previous_avg_pnl": -0.0658, "previous_win_rate": 11.1, "win_rate_delta": -11.1}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.4021, "current_avg_pnl": 0.455, "current_win_rate": 33.3, "previous_avg_pnl": 0.8571, "previous_win_rate": 27.3, "win_rate_delta": 6.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.4314, "current_avg_pnl": 0.7343, "current_win_rate": 40.0, "previous_avg_pnl": 0.3029, "previous_win_rate": 14.3, "win_rate_delta": 25.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 10, "geometry_changed_delta": 0, "geometry_preserved_delta": 4, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -15, "geometry_changed_delta": 0, "geometry_preserved_delta": 151, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2265.88, "median_terminal_delta_sec": 2266.17, "sl_rate_delta": 0.0, "win_rate_delta": 50.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
