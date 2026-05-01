# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `5170` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 12 | 12 | 10 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 7661 | 7661 | 7658 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1832802 | 1832790 | 12 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1832802 | 1832798 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1832802 | 1825141 | 7661 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1832802 | 1775076 | 57726 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1832802 | 1816547 | 16255 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1832802 | 1832802 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1832802 | 1832802 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1832802 | 1832802 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1832802 | 1830501 | 2301 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1832802 | 1780307 | 52495 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1832802 | 1802576 | 30226 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1832802 | 1832783 | 19 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1832802 | 1832797 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1832802 | 1832802 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 57726 | 57726 | 47881 | 6 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 16255 | 16255 | 16255 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 30226 | 30226 | 29125 | 4 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2301 | 2301 | 1431 | 14 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 52495 | 52495 | 26870 | 70 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 19 | 19 | 18 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1832790): breakout_not_found=603155, regime_blocked=484899, basic_filters_failed=313700, retest_proximity_failed=227329, volume_spike_missing=203705, ema_alignment_reject=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1832798): regime_blocked=1506205, sweeps_not_detected=129868, ema_alignment_reject=85521, basic_filters_failed=62294, adx_reject=35718, reclaim_confirmation_failed=7334, momentum_reject=5814, rsi_reject=44
- **EVAL::DIVERGENCE_CONTINUATION** (total=1825141): regime_blocked=1506205, cvd_divergence_failed=211914, basic_filters_failed=62294, missing_cvd=30116, ema_alignment_reject=7919, retest_proximity_failed=6693
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1775076): regime_blocked=1021300, auction_not_detected=388786, basic_filters_failed=195752, reclaim_hold_failed=96890, tail_too_small=66046, adx_reject=5274, rsi_reject=1028
- **EVAL::FUNDING_EXTREME** (total=1816547): funding_not_extreme=1295938, basic_filters_failed=435607, missing_funding_rate=52854, ema_alignment_reject=16151, rsi_reject=15997
- **EVAL::LIQUIDATION_REVERSAL** (total=1832802): cascade_threshold_not_met=1355788, basic_filters_failed=447158, cvd_divergence_failed=19585, rsi_reject=10271
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1832802): feature_disabled=1495979, regime_blocked=336823
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1832802): regime_blocked=1506205, breakout_not_found=143064, ema_alignment_reject=85521, basic_filters_failed=62294, adx_reject=35718
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1830501): regime_blocked=1347897, breakout_not_detected=209839, basic_filters_failed=133458, compression_not_detected=104051, rsi_reject=12363, macd_reject=12099, volume_reject=7389, missing_fvg_or_orderblock=3405
- **EVAL::SR_FLIP_RETEST** (total=1780307): regime_blocked=1021300, retest_out_of_zone=245033, basic_filters_failed=188842, flip_close_not_confirmed=144955, reclaim_hold_failed=119817, wick_quality_failed=30443, insufficient_candles=15628, rsi_reject=8730, missing_fvg_or_orderblock=3484, ema_alignment_reject=2075
- **EVAL::STANDARD** (total=1802576): momentum_reject=595191, basic_filters_failed=345286, sweeps_not_detected=289272, ema_alignment_reject=268100, adx_reject=251009, insufficient_candles=26944, macd_reject=12081, invalid_sl_geometry=7745, rsi_reject=6939, htf_ema_reject=9
- **EVAL::TREND_PULLBACK** (total=1832783): regime_blocked=1506205, ema_not_tested_prev=95987, ema_alignment_reject=85521, basic_filters_failed=55651, no_ema_reclaim_close=33931, body_conviction_fail=20738, insufficient_candles=15260, rsi_reject=11630, prev_already_below_emas=6806, prev_already_above_emas=1040, no_prev_high_break=9, ema21_not_tagged=2, momentum_flat=2, no_prev_low_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1832797): regime_blocked=484899, breakout_not_found=469503, retest_proximity_failed=439240, basic_filters_failed=313700, volume_spike_missing=125450, ema_alignment_reject=5
- **EVAL::WHALE_MOMENTUM** (total=1832802): momentum_reject=1347903, regime_blocked=484899

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 778672 | 46.7% |
| QUIET | 439936 | 26.4% |
| TRENDING_UP | 314260 | 18.8% |
| TRENDING_DOWN | 136046 | 8.2% |
| RANGING | 6 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **2066**
- Average confidence gap to threshold: **14.71** (samples=2066) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=810, BIOUSDT=144, XAGUSDT=136, SOLUSDT=129, ORCAUSDT=125, XAUUSDT=124, DOGEUSDT=103, XRPUSDT=95, BTCUSDT=93, CLUSDT=86

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 7711 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 232 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 139 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 396 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 29 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 7 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 190 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 504 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 179 |
| SR_FLIP_RETEST | filtered | min_confidence | 8338 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1438 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 809 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 105 |
| TREND_PULLBACK_EMA | kept | watchlist_tier_keep | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 67.35 | 80.00 | 12.65 | 20.55 | 20.00 | 18.50 | 0.00 | 3.00 |
| DIVERGENCE_CONTINUATION | kept | 3 | 60.57 | 60.00 | -0.57 | 21.07 | 19.93 | 20.00 | 1.67 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 7943 | 44.80 | 79.56 | 34.76 | 22.97 | 18.09 | 13.98 | 1.13 | 5.88 |
| FAILED_AUCTION_RECLAIM | kept | 139 | 63.61 | 50.00 | -13.61 | 23.65 | 20.00 | 14.00 | 3.54 | 0.04 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 425 | 56.70 | 66.02 | 9.32 | 20.63 | 19.86 | 15.00 | 3.02 | 1.03 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 7 | 60.44 | 50.00 | -10.44 | 22.01 | 20.00 | 15.00 | 0.71 | 1.37 |
| QUIET_COMPRESSION_BREAK | filtered | 190 | 70.42 | 80.00 | 9.58 | 19.98 | 19.90 | 15.53 | 0.00 | 1.05 |
| QUIET_COMPRESSION_BREAK | kept | 683 | 66.39 | 57.86 | -8.53 | 20.62 | 19.93 | 15.79 | 0.00 | 5.64 |
| SR_FLIP_RETEST | filtered | 9776 | 66.36 | 77.79 | 11.43 | 20.53 | 20.00 | 17.61 | 1.39 | 0.93 |
| SR_FLIP_RETEST | kept | 914 | 61.15 | 53.45 | -7.70 | 20.74 | 19.85 | 15.15 | 1.04 | 3.73 |
| TREND_PULLBACK_EMA | kept | 1 | 57.50 | 50.00 | -7.50 | 18.80 | 20.00 | 17.60 | 5.50 | 0.00 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8388116`
- `Path funnel` emissions: `309`
- `Regime distribution` emissions: `230`
- `QUIET_SCALP_BLOCK` events: `2939`
- `confidence_gate` events: `20083`

## Dependency readiness
- cvd: presence[absent=230985, present=1601817] state[empty=230985, populated=1601817] buckets[many=454964, none=230985, some=1146853] sources[none] quality[none]
- funding_rate: presence[absent=52854, present=1779948] state[empty=52854, populated=1779948] buckets[few=1779948, none=52854] sources[none] quality[none]
- liquidation_clusters: presence[absent=1832802] state[empty=1832802] buckets[none=1832802] sources[none] quality[none]
- oi_snapshot: presence[absent=21604, present=1811198] state[empty=21604, populated=1811198] buckets[many=1811198, none=21604] sources[none] quality[none]
- order_book: presence[absent=83953, present=1748849] state[populated=1748849, unavailable=83953] buckets[few=1748849, none=83953] sources[book_ticker=1748849, unavailable=83953] quality[none=83953, top_of_book_only=1748849]
- orderblocks: presence[absent=1832802] state[empty=1832802] buckets[none=1832802] sources[not_implemented=1832802] quality[none]
- recent_ticks: presence[absent=91343, present=1741459] state[empty=91343, populated=1741459] buckets[many=1741459, none=91343] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.0813689231872559` sec
- Median create→first breach: `None` sec
- Median create→terminal: `606.2377600669861` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.2838 | None | 610.3321421146393 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 0.0 | 0.0 | -0.0442 | None | 604.8341341018677 |
| SR_FLIP_RETEST | 5 | 5 | 0.0 | 0.0 | 0.0 | -0.0265 | None | 607.5723850727081 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 52495 | 70 | 26870 | 0.0 | 0.0 | None | 607.5723850727081 | 25625 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 19 | 1 | 18 | 0.0 | 0.0 | None | None | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `63`
- Gating Δ: `45428`
- No-generation Δ: `1153354`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0015, "current_avg_pnl": -0.0442, "current_win_rate": 0.0, "previous_avg_pnl": -0.0457, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0265, "current_avg_pnl": -0.0265, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 60, "geometry_changed_delta": 0, "geometry_preserved_delta": 19043, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 607.57, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
