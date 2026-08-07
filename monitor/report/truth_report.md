# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `2294` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 200 | 200 | 181 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 22317 | 22317 | 21350 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 132698 | 132698 | 22 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 112941 | 112949 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 112534 | 108423 | 4502 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 112974 | 112561 | 470 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 115841 | 115669 | 210 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 106837 | 106846 | 6 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 113038 | 113076 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 113090 | 109777 | 4463 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 137558 | 142065 | 1078 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 132722 | 123771 | 13741 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 115550 | 115561 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 112954 | 112968 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 112475 | 112044 | 485 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 114251 | 111969 | 2921 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 112166 | 112369 | 66 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 103687 | 100879 | 2992 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 103878 | 103302 | 660 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 132656 | 132661 | 31 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 106852 | 106868 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1870 | 1870 | 1685 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1094 | 1094 | 254 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 27 | 27 | 27 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14387 | 14387 | 14041 | 15 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 13 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13338 | 13338 | 11451 | 11 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2949 | 2949 | 1143 | 44 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 44511 | 44511 | 30483 | 287 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3491 | 3491 | 2378 | 15 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 8300 | 8300 | 7871 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 592 | 592 | 516 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3268 | 3268 | 3038 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 117 | 117 | 19 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 498 | 498 | 86 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=132698): breakout_not_found=58881, basic_filters_failed=52664, move_not_fresh=15364, breakout_stale=4059, retest_proximity_failed=1357, volume_spike_missing=149, ema_alignment_reject=143, missing_fvg_or_orderblock=43, rsi_reject=23, move_exhausted=15
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=112949): cls_disabled_merged_into_lsr=112949
- **EVAL::DIVERGENCE_CONTINUATION** (total=108423): basic_filters_failed=41996, cvd_divergence_failed=33672, h1_trend_not_aligned=22090, ema_alignment_reject=7981, retest_proximity_failed=1792, missing_fvg_or_orderblock=559, regime_blocked=333
- **EVAL::FAILED_AUCTION_RECLAIM** (total=112561): auction_not_detected=64427, basic_filters_failed=38991, regime_blocked=6732, reclaim_hold_failed=1405, tail_too_small=1004, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=115669): funding_not_extreme=62745, basic_filters_failed=41560, missing_funding_rate=8436, ema_alignment_reject=1852, rsi_reject=718, cvd_divergence_failed=183, momentum_reject=161, missing_fvg_or_orderblock=14
- **EVAL::LIQUIDATION_REVERSAL** (total=106846): cascade_threshold_not_met=61568, basic_filters_failed=43651, cvd_divergence_failed=1051, rsi_reject=535, missing_fvg_or_orderblock=39, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=113076): no_ma_cross=69247, basic_filters_failed=42025, ma_cross_cooldown=1584, ma_cross_htf_misaligned=220
- **EVAL::MEAN_REVERT** (total=109777): no_extension=84878, basic_filters_failed=24899
- **EVAL::MOVER_AVWAP_SCALP** (total=142065): basic_filters_failed=52885, no_avwap_tag=40379, no_mover_leg=35809, avwap_slope_against=8307, avwap_reclaim_no_volume=2666, no_avwap_reclaim=1885, anchor_too_recent=134
- **EVAL::MOVER_TREND_PULLBACK** (total=123771): basic_filters_failed=52762, mover_run_too_small=49844, no_reclaim=17397, no_pullback_tag=3714, insufficient_candles=54
- **EVAL::OPENING_RANGE_BREAKOUT** (total=115561): feature_disabled=115561
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=112968): regime_blocked=87472, breakout_not_found=15441, basic_filters_failed=8342, adx_reject=1701, ema_alignment_reject=12
- **EVAL::QUIET_COMPRESSION_BREAK** (total=112044): compression_not_detected=34199, regime_blocked=32140, basic_filters_failed=30631, breakout_not_detected=13699, volume_confirmation_failed=1223, rsi_reject=147, missing_fvg_or_orderblock=5
- **EVAL::RANGE_FADE** (total=111969): no_range_edge=87069, basic_filters_failed=24900
- **EVAL::SR_FLIP_RETEST** (total=112369): flip_close_not_confirmed=64081, basic_filters_failed=38962, regime_blocked=6708, h1_break_not_confirmed=898, long_break_volume_thin=765, retest_out_of_zone=642, reclaim_hold_failed=125, long_acceptance_not_held=124, wick_quality_failed=26, ema_alignment_reject=23, whipsaw_flip=13, missing_fvg_or_orderblock=2
- **EVAL::STANDARD** (total=100879): momentum_reject=28894, adx_reject=24822, basic_filters_failed=17243, sweeps_not_detected=11880, macd_reject=9398, ema_alignment_reject=4128, htf_poi_unanchored=3851, rsi_reject=537, invalid_sl_geometry=121, mtf_reject=5
- **EVAL::TREND_PULLBACK** (total=103302): h1_trend_not_aligned=30067, basic_filters_failed=23335, h1_pullback_not_confirmed=17338, ema_alignment_reject=11393, ema_not_tested_prev=6641, no_ema_reclaim_close=5844, body_conviction_fail=3334, rsi_reject=2735, prev_already_below_emas=689, regime_blocked=602, prev_already_above_emas=401, no_prev_low_break=307, no_prev_high_break=305, momentum_flat=174, missing_fvg_or_orderblock=69, ema21_not_tagged=49, momentum_reject=19
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=132661): breakout_not_found=60046, basic_filters_failed=52660, move_not_fresh=12350, breakout_stale=4271, retest_proximity_failed=2563, volume_spike_missing=641, move_exhausted=69, ema_alignment_reject=25, rsi_reject=21, missing_fvg_or_orderblock=15
- **EVAL::WHALE_MOMENTUM** (total=106868): momentum_reject=85290, recent_ticks_insufficient=12726, basic_filters_failed=8852

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=29): execution:overextended=29
- **DIVERGENCE_CONTINUATION** (total=1390): setup_compat:regime_VOLATILE_UNSUITABLE=1353, setup_compat:regime_BREAKOUT_EXPANSION=37
- **FAILED_AUCTION_RECLAIM** (total=836): execution:overextended=557, setup_compat:regime_STRONG_TREND=180, context_floor=95, setup_compat:regime_VOLATILE_UNSUITABLE=4
- **FUNDING_EXTREME_SIGNAL** (total=972): execution:trigger_not_confirmed=871, context_floor=101
- **LIQUIDATION_REVERSAL** (total=27): execution:trigger_not_confirmed=27
- **LIQUIDITY_SWEEP_REVERSAL** (total=3832): execution:overextended=1609, execution:trigger_not_confirmed=1380, setup_compat:regime_STRONG_TREND=843
- **MA_CROSS_TREND_SHIFT** (total=16): setup_compat:regime_DIRTY_RANGE=5, execution:trigger_not_confirmed=5, setup_compat:regime_CLEAN_RANGE=4, execution:overextended=2
- **MEAN_REVERT** (total=3972): setup_compat:regime_STRONG_TREND=1722, setup_compat:regime_WEAK_TREND=1228, execution:overextended=1022
- **MOVER_AVWAP_SCALP** (total=1770): execution:overextended=1308, execution:trigger_not_confirmed=286, entry_quality=176
- **MOVER_TREND_PULLBACK** (total=26067): execution:overextended=13736, execution:trigger_not_confirmed=10965, entry_quality=1366
- **QUIET_COMPRESSION_BREAK** (total=998): context_floor=789, execution:trigger_not_confirmed=209
- **RANGE_FADE** (total=3359): setup_compat:regime_STRONG_TREND=1029, setup_compat:regime_WEAK_TREND=999, execution:overextended=699, setup_compat:regime_VOLATILE_UNSUITABLE=583, context_edge=44, setup_compat:regime_BREAKOUT_EXPANSION=5
- **TREND_PULLBACK_EMA** (total=3070): setup_compat:regime_CLEAN_RANGE=2032, setup_compat:regime_DIRTY_RANGE=863, setup_compat:regime_VOLATILE_UNSUITABLE=146, entry_quality=29
- **VOLUME_SURGE_BREAKOUT** (total=58): execution:overextended=48, context_floor=10
- **WHALE_MOMENTUM** (total=412): execution:trigger_not_confirmed=412

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 292738 | 37.2% |
| QUIET | 213297 | 27.1% |
| TRENDING_UP | 128921 | 16.4% |
| TRENDING_DOWN | 87075 | 11.1% |
| VOLATILE | 64334 | 8.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **203**
- Average confidence gap to threshold: **11.54** (samples=203) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=30, ETHUSDT=27, AVAXUSDT=26, TRXUSDT=22, BTCUSDT=13, NEARUSDT=12, AAVEUSDT=11, ADAUSDT=7, BNBUSDT=7, 1000PEPEUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 19 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 147 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 18 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 35 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 31 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 66 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 31 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 72 |
| MEAN_REVERT | filtered | min_confidence | 20 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 7 |
| MEAN_REVERT | kept | min_confidence_pass | 11 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 497 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 42 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 717 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2500 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5517 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 148 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 9 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 51 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 7 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 19 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 121 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 28 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 12 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 19 | 72.85 | 65.00 | -7.85 | 21.20 | 18.05 | 20.00 | 4.50 | 2.84 |
| DIVERGENCE_CONTINUATION | filtered | 165 | 55.84 | 64.35 | 8.51 | 19.73 | 19.90 | 17.59 | 0.94 | 14.08 |
| DIVERGENCE_CONTINUATION | kept | 35 | 73.20 | 65.00 | -8.20 | 19.93 | 19.51 | 18.05 | 0.69 | 1.68 |
| FAILED_AUCTION_RECLAIM | filtered | 13 | 55.00 | 60.00 | 5.00 | 20.20 | 20.00 | 20.00 | 1.00 | 11.00 |
| FAILED_AUCTION_RECLAIM | kept | 31 | 68.69 | 65.00 | -3.69 | 20.29 | 17.75 | 20.00 | 1.58 | 1.90 |
| FUNDING_EXTREME_SIGNAL | filtered | 66 | 51.51 | 65.00 | 13.49 | 20.08 | 15.16 | 17.73 | 2.67 | 2.85 |
| FUNDING_EXTREME_SIGNAL | kept | 10 | 68.42 | 65.00 | -3.42 | 20.48 | 16.36 | 17.30 | 2.50 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 35 | 49.23 | 64.43 | 15.20 | 19.85 | 19.73 | 18.66 | 1.60 | 20.62 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 72 | 72.89 | 65.00 | -7.89 | 20.17 | 18.07 | 18.01 | 0.54 | 0.00 |
| MEAN_REVERT | filtered | 27 | 53.09 | 61.85 | 8.76 | 21.01 | 17.30 | 17.95 | 0.00 | 0.74 |
| MEAN_REVERT | kept | 11 | 70.97 | 65.00 | -5.97 | 20.03 | 15.83 | 16.39 | 0.00 | -0.27 |
| MOVER_AVWAP_SCALP | filtered | 539 | 54.08 | 60.51 | 6.43 | 19.99 | 14.41 | 15.80 | 3.13 | 8.14 |
| MOVER_AVWAP_SCALP | kept | 717 | 78.01 | 65.00 | -13.01 | 20.31 | 16.89 | 15.80 | 4.46 | 1.12 |
| MOVER_TREND_PULLBACK | filtered | 2503 | 56.68 | 64.16 | 7.48 | 19.44 | 18.09 | 15.80 | 4.28 | 19.23 |
| MOVER_TREND_PULLBACK | kept | 5517 | 77.05 | 65.00 | -12.05 | 20.18 | 18.28 | 15.80 | 4.38 | 1.88 |
| QUIET_COMPRESSION_BREAK | filtered | 157 | 52.99 | 65.00 | 12.01 | 21.14 | 19.47 | 20.00 | 0.00 | 9.95 |
| QUIET_COMPRESSION_BREAK | kept | 51 | 77.93 | 65.00 | -12.93 | 21.61 | 19.86 | 20.00 | 0.00 | -1.71 |
| RANGE_FADE | kept | 1 | 76.30 | 65.00 | -11.30 | 21.10 | 15.00 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 49.07 | 65.00 | 15.93 | 20.83 | 20.00 | 16.74 | 1.21 | 20.57 |
| SR_FLIP_RETEST | kept | 1 | 68.00 | 65.00 | -3.00 | 20.00 | 20.00 | 15.20 | 3.50 | 3.50 |
| TREND_PULLBACK_EMA | filtered | 23 | 56.39 | 65.00 | 8.61 | 20.61 | 19.30 | 17.20 | 5.09 | 13.29 |
| TREND_PULLBACK_EMA | kept | 121 | 74.86 | 65.00 | -9.86 | 20.54 | 19.84 | 18.65 | 5.07 | 0.10 |
| VOLUME_SURGE_BREAKOUT | filtered | 28 | 54.52 | 64.82 | 10.30 | 20.93 | 19.84 | 20.00 | 4.00 | 3.71 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.40 | 65.00 | -13.40 | 20.85 | 16.95 | 20.00 | 5.75 | 1.50 |
| WHALE_MOMENTUM | filtered | 12 | 58.56 | 65.00 | 6.44 | 22.31 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 19 | 72.85 | 18.68 | 15.47 | 12.00 | 12.74 | 5.00 | 7.30 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 165 | 55.84 | 22.38 | 11.39 | 7.62 | 13.47 | 5.94 | 8.26 | 0.94 |
| DIVERGENCE_CONTINUATION | kept | 35 | 73.20 | 22.49 | 13.49 | 9.77 | 15.69 | 4.73 | 8.21 | 0.69 |
| FAILED_AUCTION_RECLAIM | filtered | 13 | 55.00 | 15.00 | 18.00 | 3.69 | 13.31 | 5.00 | 10.00 | 1.00 |
| FAILED_AUCTION_RECLAIM | kept | 31 | 68.69 | 19.52 | 18.00 | 4.26 | 11.39 | 6.06 | 9.78 | 1.58 |
| FUNDING_EXTREME_SIGNAL | filtered | 66 | 51.51 | 24.03 | 10.48 | 5.55 | 12.74 | 8.45 | 4.30 | 2.67 |
| FUNDING_EXTREME_SIGNAL | kept | 10 | 68.42 | 24.20 | 12.20 | 3.00 | 12.50 | 7.75 | 6.27 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 35 | 49.23 | 21.69 | 15.49 | 8.74 | 11.11 | 4.60 | 6.61 | 1.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 72 | 72.89 | 20.81 | 14.72 | 9.88 | 15.00 | 5.15 | 6.80 | 0.54 |
| MEAN_REVERT | filtered | 27 | 53.09 | 24.11 | 17.56 | 5.00 | 12.00 | 4.91 | 4.70 | 0.00 |
| MEAN_REVERT | kept | 11 | 70.97 | 22.82 | 16.55 | 7.36 | 12.00 | 6.95 | 5.29 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 539 | 54.08 | 18.83 | 18.19 | 8.77 | 13.02 | 5.92 | 5.34 | 3.13 |
| MOVER_AVWAP_SCALP | kept | 717 | 78.01 | 19.08 | 18.12 | 9.47 | 13.64 | 5.94 | 8.72 | 4.46 |
| MOVER_TREND_PULLBACK | filtered | 2503 | 56.68 | 17.92 | 18.12 | 7.87 | 13.55 | 5.53 | 9.20 | 4.28 |
| MOVER_TREND_PULLBACK | kept | 5517 | 77.05 | 19.64 | 18.14 | 8.39 | 13.38 | 5.88 | 9.16 | 4.38 |
| QUIET_COMPRESSION_BREAK | filtered | 157 | 52.99 | 19.09 | 17.77 | 11.46 | 13.89 | 5.68 | 4.47 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 51 | 77.93 | 17.47 | 17.76 | 14.24 | 14.06 | 5.49 | 9.37 | 0.00 |
| RANGE_FADE | kept | 1 | 76.30 | 25.00 | 18.00 | 6.00 | 12.00 | 10.00 | 5.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 49.07 | 18.14 | 8.00 | 13.29 | 14.00 | 5.00 | 10.00 | 1.21 |
| SR_FLIP_RETEST | kept | 1 | 68.00 | 25.00 | 18.00 | 3.00 | 11.00 | 5.00 | 6.00 | 3.50 |
| TREND_PULLBACK_EMA | filtered | 23 | 56.39 | 6.57 | 18.00 | 7.50 | 15.17 | 8.09 | 9.27 | 5.09 |
| TREND_PULLBACK_EMA | kept | 121 | 74.86 | 15.16 | 18.00 | 7.60 | 14.50 | 5.86 | 8.86 | 5.07 |
| VOLUME_SURGE_BREAKOUT | filtered | 28 | 54.52 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 6.70 | 4.00 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.40 | 25.00 | 16.00 | 13.50 | 14.00 | 5.00 | 8.15 | 5.75 |
| WHALE_MOMENTUM | filtered | 12 | 58.56 | 25.00 | 8.00 | 7.50 | 11.17 | 8.33 | 8.56 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 19 | 72.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 165 | 55.84 | 0.00 | 0.00 | 1.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.18** |
| DIVERGENCE_CONTINUATION | kept | 35 | 73.20 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.14** |
| FAILED_AUCTION_RECLAIM | filtered | 13 | 55.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 31 | 68.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 66 | 51.51 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.73** |
| FUNDING_EXTREME_SIGNAL | kept | 10 | 68.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 35 | 49.23 | 0.00 | 0.00 | 0.00 | 0.00 | 3.84 | 0.00 | 0.00 | 0.00 | **3.84** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 72 | 72.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 27 | 53.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 11 | 70.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 539 | 54.08 | 4.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.68 | **6.94** |
| MOVER_AVWAP_SCALP | kept | 717 | 78.01 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | **0.12** |
| MOVER_TREND_PULLBACK | filtered | 2503 | 56.68 | 0.00 | 0.00 | 1.06 | 0.00 | 0.30 | 0.00 | 0.00 | 0.08 | **1.44** |
| MOVER_TREND_PULLBACK | kept | 5517 | 77.05 | 0.00 | 0.00 | 0.70 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.88** |
| QUIET_COMPRESSION_BREAK | filtered | 157 | 52.99 | 0.00 | 0.00 | 1.46 | 0.00 | 0.44 | 0.00 | 0.00 | 6.12 | **8.02** |
| QUIET_COMPRESSION_BREAK | kept | 51 | 77.93 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.42 | **0.58** |
| RANGE_FADE | kept | 1 | 76.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 7 | 49.07 | 0.00 | 0.00 | 2.06 | 0.00 | 18.51 | 0.00 | 0.00 | 0.00 | **20.57** |
| SR_FLIP_RETEST | kept | 1 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 23 | 56.39 | 0.00 | 0.00 | 4.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.94** |
| TREND_PULLBACK_EMA | kept | 121 | 74.86 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.16** |
| VOLUME_SURGE_BREAKOUT | filtered | 28 | 54.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 12 | 58.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **124049 held of 169470 seen** across 21 strategies; 2786 cells past the sample floor; **700 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 29418 | 181/29237/0 | 52% | -0.02 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 16975 | 24/16951/0 | 51% | -0.00 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16541 | 1/16540/0 | 47% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11164 | 4/11160/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.42R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 8929 | 0/8929/0 | 51% | -0.05 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.37R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 7067 | 26/7041/0 | 31% | -0.39 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| SHADOW_MEAN_REVERT | 4475 | 0/0/4475 | 42% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.95R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-0.99R) |
| LIQUIDITY_SWEEP_REVERSAL | 4454 | 11/4443/0 | 45% | -0.20 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.54R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| TREND_PULLBACK_EMA | 4242 | 2/4240/0 | 50% | -0.22 | LONDON/QUIET/NORMAL/BTC_NEUTRAL (+0.74R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_RANGE_FADE | 4092 | 0/0/4092 | 40% | +0.13 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.02R) |
| MEAN_REVERT | 3841 | 0/3841/0 | 75% | +0.47 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| SHADOW_FUNDING_FADE | 3745 | 0/0/3745 | 39% | -0.33 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.27R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-0.90R) |
| RANGE_FADE | 3179 | 0/3179/0 | 28% | -0.47 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | NY/MARKUP/NORMAL/BTC_RISING (-1.31R) |
| VOLUME_SURGE_BREAKOUT | 2053 | 13/2040/0 | 43% | +0.02 | LONDON/MARKUP/COMPRESSED/BTC_NEUTRAL (+1.87R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1739 | 4/1735/0 | 33% | -0.38 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (-1.61R) |
| WHALE_MOMENTUM | 1250 | 0/1250/0 | 47% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 413 | 0/0/413 | 46% | -0.19 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.81R) |
| BREAKDOWN_SHORT | 321 | 7/314/0 | 60% | +0.31 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| LIQUIDATION_REVERSAL | 66 | 0/66/0 | 64% | -0.48 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| MA_CROSS_TREND_SHIFT | 18 | 1/17/0 | 28% | -0.46 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` +1.87R (n=50, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP` -1.61R (n=20, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 73 | 37% / -0.33R | 73 | 53% / -0.11R | +0.22 | **ATR** |
| TREND_PULLBACK_EMA | 132 | 43% / -0.27R | 132 | 48% / -0.12R | +0.16 | **ATR** |
| SR_FLIP_RETEST | 2760 | 46% / -0.20R | 2760 | 49% / -0.10R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 405 | 38% / -0.23R | 405 | 41% / -0.13R | +0.10 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 67 | 42% / +0.02R | 67 | 48% / -0.05R | -0.07 | **FIXED** |
| DIVERGENCE_CONTINUATION | 774 | 47% / -0.12R | 774 | 52% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 650 | 50% / -0.17R | 650 | 54% / -0.12R | +0.05 | **ATR** |
| MEAN_REVERT | 365 | 54% / +0.01R | 365 | 50% / +0.06R | +0.05 | **ATR** |
| MOVER_TREND_PULLBACK | 3452 | 52% / -0.05R | 3452 | 54% / -0.01R | +0.04 | **ATR** |
| RANGE_FADE | 210 | 16% / -0.72R | 210 | 18% / -0.68R | +0.04 | **ATR** |
| WHALE_MOMENTUM | 89 | 49% / -0.25R | 89 | 48% / -0.27R | -0.03 | **FIXED** |
| BREAKDOWN_SHORT | 16 | 25% / -0.32R | 16 | 25% / -0.30R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1307 | 45% / -0.13R | 1307 | 45% / -0.15R | -0.01 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2241 | 47% / -0.10R | 2241 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 9 | 33% / -0.27R | 9 | 33% / -0.27R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 40% / -0.81R | 5 | 40% / -0.40R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4557 | 30% | -0.14R | 272 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 395 | 40% | -0.14R | 118 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 24 | 54% | +0.05R | 16 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1216 | 28% / -1.70R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 11 | 18% / -0.81R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3434 | 38% / -0.23R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 938 | 33% / -0.58R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 61 | 21% / -0.98R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 577 | 30% / -1.90R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 730 | 35% / -0.12R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 278 | 41% / -1.31R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 84 | 31% / -1.28R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 130 | 25% / -1.06R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 359 | 31% / -0.17R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 10 | 20% / -0.43R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 98 | 36% / -0.35R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 46 | 43% / -0.13R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 5 | 20% / -1.42R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 21 | 38% / -0.40R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 42 · alerting: **6** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 178/6) (sustained 178 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 3859x (gate reads 0x, withheld 0x — refusal dark); last EPICUSDT age=18752.6s (streak 57/6) (sustained 57 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.39R (bound 0.3) (streak 178/6) (sustained 178 cycles)
- **ALERT** `mean_revert_emission` — 1043 detections since last emission (emitted_total=9) — and the POST-SCORING blocked candidates measure +0.47R over n=3841, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 26/6) (sustained 26 cycles)
- **ALERT** `tuned_variants` — 299 non-stamps — atr_arm_uncomputable=299 (seen=4189 stamped=371 skipped=3519) (streak 178/6) (sustained 178 cycles)
- **ALERT** `auto_dispatch` — 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: tier=18) (streak 141/3) (sustained 141 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 21597698 accepted, 0 rejected | 0 |
| auto_dispatch | violating | 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: tier=18) (streak 141/3) | 141 |
| btc_reference | ok | BTC ref 64278.70 | 0 |
| candle_coverage | ok | 102/111 symbols with ≥20 15m candles, 89/111 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 1504 dup bars, 0 undedupable; ws 0 out-of-order, 144 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 178/6) | 178 |
| context_emission_policy | ok | output +40 / upstream +45 | 0 |
| dark_resolution | ok | 66 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4592476 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.39R (bound 0.3) (streak 178/6) | 178 |
| emission_controller | ok | last cycle 1351s ago; live_overrides=24 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=13 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4024 stamps (MEAN_REVERT=491, MOVER_AVWAP_SCALP=301, MOVER_TREND_PULLBACK=2554, RANGE_FADE=385, TREND_PULLBACK_EMA=293), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +1 / upstream +1 | 0 |
| geometry_ab | ok | output +5 / upstream +414 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1043 detections since last emission (emitted_total=9) — and the POST-SCORING blocked candidates measure +0.47R over n=3841, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 26/6) | 26 |
| mean_revert_path | ok | output +102 / upstream +414 | 0 |
| mover_admission_metadata | ok | 854 symbols known, 153 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 189189 evicted (sampled: execution:trigger_not_confirmed 400/64361, execution:overextended 400/63662, setup_compat:regime_STRONG_TREND 400/26370) | 0 |
| price_action_lane | ok | 555562 evaluated, 323 emitted; cooldown=54443, delta_opposed=40865, no_footprint=186403, no_opposing_target=4083, no_sweep=235307, rr_below_floor=34138 | 0 |
| promoted_pair_integrity | ok | 18/18 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.47R over n=3179 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +9 / upstream +414 | 0 |
| sar_alignment_crosscheck | ok | 327/11711 disagreed (2.8%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +414 | 0 |
| sar_ledger_candles | ok | 13/68 unfetchable (19%); top cause: gap or duplicate bar in the 15m window; symbols: HFTUSDT, LDOUSDT, SKYAIUSDT, TAKEUSDT, TRXUSDT +2 more | 0 |
| sar_live_arms | ok | 1 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 469 records await one (55 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| setup_tf_resolver | ok | 148961 resolutions, 76956 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 3859x (gate reads 0x, withheld 0x — refusal dark); last EPICUSDT age=18752.6s (streak 57/6) | 57 |
| staleness_v2_shadow | ok | output +2 / upstream +2 | 0 |
| strategy_edge | ok | output +107 / upstream +414 | 0 |
| structural_snap | ok | 369/369 measured, 4 blind, 0 levels moved (refusals: redetect_cooldown=806) | 0 |
| structural_veto_lane | ok | 1129 stamped; 0 with no readable level book, 156 with clear air ahead, 762 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +414 / upstream +45 | 0 |
| tuned_variants | violating | 299 non-stamps — atr_arm_uncomputable=299 (seen=4189 stamped=371 skipped=3519) (streak 178/6) | 178 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3570842`
- `Path funnel` emissions: `94`
- `Regime distribution` emissions: `94`
- `QUIET_SCALP_BLOCK` events: `203`
- `confidence_gate` events: `10163`
- `free_channel_post` events: `28`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **19**
- Total REST-fallback activations: **4**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 6 | 2800 | 5252 | 61518 | 0 |
| futures_aggtrade | 4 | 1858 | 3238 | 3456 | 0 |
| futures_depth | 4 | 2152 | 2201 | 4104 | 0 |
| futures_liq | 2 | 1868 | 1868 | 2028 | 0 |
| futures_mover | 3 | 4689 | 4689 | 232863 | 1 |

| Label | REST-fallback activations |
|---|---:|
| futures | 4 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **28**

| Source | Count |
|---|---:|
| signal_close | 21 |
| regime_shift | 6 |
| signal_highlight | 1 |

- By severity: HIGH=28

## Dependency readiness
- cvd: presence[present=598115] state[populated=598115] buckets[many=598115] sources[none] quality[none]
- funding_rate: presence[absent=81163, present=516952] state[empty=81163, populated=516952] buckets[few=516952, none=81163] sources[none] quality[none]
- liquidation_clusters: presence[absent=339544, present=258571] state[empty=339544, populated=258571] buckets[few=199360, none=339544, some=59211] sources[none] quality[none]
- oi_snapshot: presence[absent=76609, present=521506] state[empty=76609, populated=521506] buckets[many=521506, none=76609] sources[none] quality[none]
- order_book: presence[absent=164859, present=433256] state[populated=433256, unavailable=164859] buckets[few=433256, none=164859] sources[book_ticker=433256, unavailable=164859] quality[none=164859, top_of_book_only=433256]
- orderblocks: presence[absent=598115] state[empty=598115] buckets[none=598115] sources[measured_dark=598115] quality[none]
- recent_ticks: presence[absent=598, present=597517] state[empty=598, populated=597517] buckets[many=597517, none=598] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.183456897735596` sec
- Median create→first breach: `1573.221762895584` sec
- Median create→terminal: `1573.4682190418243` sec
- Median first breach→terminal: `1.4307801723480225` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 4.8}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 3.485259156968487 | 3.0 | 1.161753052322829 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.8966147998574607 | 3.0 | 0.2988715999524869 | 0 | 1 |
| MOVER_TREND_PULLBACK | 19 | 19 | 4.041409395260044 | 3.0 | 1.3471364650866813 | 15 | 4 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 4.7429 | 396.44940996170044 | 397.74343609809875 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 5.1847 | 1319.1340210437775 | 1319.6117630004883 |
| MOVER_TREND_PULLBACK | 19 | 19 | 0.0 | 47.4 | 0.0 | 0.0 | -0.7373 | 2026.0634150505066 | 2026.543293952942 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 592 | 1 | 516 | 0.0 | 0.0 | None | None | 76 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3268 | 16 | 3038 | 0.0 | 0.0 | None | None | 230 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `11`
- Gating Δ: `6432`
- No-generation Δ: `-79851`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.5491, "current_avg_pnl": -0.7373, "current_win_rate": 0.0, "previous_avg_pnl": -0.1882, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 17, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -185, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
