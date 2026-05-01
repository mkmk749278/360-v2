# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `2823` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 12 | 12 | 10 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 5 | 5 | 4 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6367 | 6367 | 6364 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1825533 | 1825521 | 12 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1825533 | 1825528 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1825533 | 1819166 | 6367 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1825533 | 1775820 | 49713 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1825533 | 1812663 | 12870 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1825533 | 1825533 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1825533 | 1825533 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1825533 | 1825533 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1825533 | 1823533 | 2000 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1825533 | 1780601 | 44932 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1825533 | 1798708 | 26825 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1825533 | 1825514 | 19 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1825533 | 1825529 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1825533 | 1825533 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 49713 | 49713 | 41504 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 12870 | 12870 | 12870 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 26825 | 26825 | 25792 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2000 | 2000 | 1417 | 10 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 44932 | 44932 | 23620 | 67 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 19 | 19 | 18 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1825521): breakout_not_found=494966, regime_blocked=473363, volume_spike_missing=345908, basic_filters_failed=324610, retest_proximity_failed=186672, ema_alignment_reject=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1825528): regime_blocked=1538518, sweeps_not_detected=113855, ema_alignment_reject=73211, basic_filters_failed=56620, adx_reject=32112, reclaim_confirmation_failed=6040, momentum_reject=5128, rsi_reject=44
- **EVAL::DIVERGENCE_CONTINUATION** (total=1819166): regime_blocked=1538518, cvd_divergence_failed=186728, basic_filters_failed=56620, missing_cvd=25317, ema_alignment_reject=6553, retest_proximity_failed=5430
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1775820): regime_blocked=1065149, auction_not_detected=367610, basic_filters_failed=179649, reclaim_hold_failed=93190, tail_too_small=60172, adx_reject=8899, rsi_reject=1151
- **EVAL::FUNDING_EXTREME** (total=1812663): funding_not_extreme=1279403, basic_filters_failed=438333, missing_funding_rate=54749, ema_alignment_reject=20344, rsi_reject=19834
- **EVAL::LIQUIDATION_REVERSAL** (total=1825533): cascade_threshold_not_met=1352536, basic_filters_failed=447639, cvd_divergence_failed=16349, rsi_reject=9009
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1825533): feature_disabled=1272633, regime_blocked=552900
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1825533): regime_blocked=1538518, breakout_not_found=125072, ema_alignment_reject=73211, basic_filters_failed=56620, adx_reject=32112
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1823533): regime_blocked=1352164, breakout_not_detected=204457, basic_filters_failed=123029, compression_not_detected=99439, macd_reject=16776, rsi_reject=12775, volume_reject=11442, missing_fvg_or_orderblock=3451
- **EVAL::SR_FLIP_RETEST** (total=1780601): regime_blocked=1065149, retest_out_of_zone=225149, basic_filters_failed=173404, flip_close_not_confirmed=151914, reclaim_hold_failed=106386, wick_quality_failed=29260, insufficient_candles=14415, rsi_reject=9664, missing_fvg_or_orderblock=3368, ema_alignment_reject=1892
- **EVAL::STANDARD** (total=1798708): momentum_reject=614421, basic_filters_failed=350484, sweeps_not_detected=288432, ema_alignment_reject=247703, adx_reject=244174, insufficient_candles=26099, rsi_reject=10633, macd_reject=10217, invalid_sl_geometry=6536, htf_ema_reject=9
- **EVAL::TREND_PULLBACK** (total=1825514): regime_blocked=1538518, ema_not_tested_prev=84911, ema_alignment_reject=73211, basic_filters_failed=50638, no_ema_reclaim_close=30175, body_conviction_fail=17359, insufficient_candles=14051, rsi_reject=9990, prev_already_below_emas=5607, prev_already_above_emas=1038, no_prev_high_break=10, momentum_flat=3, ema21_not_tagged=2, no_prev_low_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1825529): regime_blocked=473363, breakout_not_found=390384, retest_proximity_failed=372334, basic_filters_failed=324610, volume_spike_missing=264833, ema_alignment_reject=5
- **EVAL::WHALE_MOMENTUM** (total=1825533): momentum_reject=1352170, regime_blocked=473363

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 609031 | 43.7% |
| QUIET | 390594 | 28.0% |
| TRENDING_UP | 282282 | 20.2% |
| TRENDING_DOWN | 112713 | 8.1% |
| RANGING | 6 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1822**
- Average confidence gap to threshold: **15.01** (samples=1822) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=759, XAGUSDT=132, BIOUSDT=115, XAUUSDT=106, SOLUSDT=101, ORCAUSDT=101, DOGEUSDT=97, BTCUSDT=79, XRPUSDT=76, ETHUSDT=71

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 6469 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 198 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 138 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 335 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 24 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 5 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 189 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 301 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 93 |
| SR_FLIP_RETEST | filtered | min_confidence | 6978 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1289 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 624 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 5 |
| TREND_PULLBACK_EMA | kept | watchlist_tier_keep | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 67.35 | 80.00 | 12.65 | 20.55 | 20.00 | 18.50 | 0.00 | 3.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 1 | 66.00 | 80.00 | 14.00 | 24.00 | 20.00 | 15.20 | 0.00 | 6.00 |
| DIVERGENCE_CONTINUATION | kept | 3 | 60.57 | 60.00 | -0.57 | 21.07 | 19.93 | 20.00 | 1.67 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 6667 | 44.88 | 79.55 | 34.67 | 22.96 | 18.10 | 13.98 | 1.15 | 5.85 |
| FAILED_AUCTION_RECLAIM | kept | 138 | 63.62 | 50.00 | -13.62 | 23.65 | 20.00 | 14.00 | 3.53 | 0.04 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 359 | 56.38 | 66.00 | 9.62 | 20.70 | 19.86 | 14.95 | 2.99 | 1.28 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 5 | 59.02 | 50.00 | -9.02 | 20.98 | 20.00 | 14.92 | 1.00 | 1.92 |
| QUIET_COMPRESSION_BREAK | filtered | 189 | 70.41 | 80.00 | 9.59 | 19.95 | 19.93 | 15.42 | 0.00 | 1.05 |
| QUIET_COMPRESSION_BREAK | kept | 394 | 65.40 | 57.08 | -8.32 | 20.54 | 19.88 | 15.79 | 0.00 | 3.04 |
| SR_FLIP_RETEST | filtered | 8267 | 66.50 | 77.66 | 11.16 | 20.56 | 20.00 | 17.57 | 1.35 | 0.73 |
| SR_FLIP_RETEST | kept | 629 | 57.63 | 50.24 | -7.39 | 21.58 | 19.92 | 15.12 | 0.81 | 3.46 |
| TREND_PULLBACK_EMA | kept | 1 | 57.50 | 50.00 | -7.50 | 18.80 | 20.00 | 17.60 | 5.50 | 0.00 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8318191`
- `Path funnel` emissions: `307`
- `Regime distribution` emissions: `191`
- `QUIET_SCALP_BLOCK` events: `2405`
- `confidence_gate` events: `16655`

## Dependency readiness
- cvd: presence[absent=219715, present=1605818] state[empty=219715, populated=1605818] buckets[many=442818, none=219715, some=1163000] sources[none] quality[none]
- funding_rate: presence[absent=54749, present=1770784] state[empty=54749, populated=1770784] buckets[few=1770784, none=54749] sources[none] quality[none]
- liquidation_clusters: presence[absent=1825533] state[empty=1825533] buckets[none=1825533] sources[none] quality[none]
- oi_snapshot: presence[absent=11590, present=1813943] state[empty=11590, populated=1813943] buckets[many=1813943, none=11590] sources[none] quality[none]
- order_book: presence[absent=94687, present=1730846] state[populated=1730846, unavailable=94687] buckets[few=1730846, none=94687] sources[book_ticker=1730846, unavailable=94687] quality[none=94687, top_of_book_only=1730846]
- orderblocks: presence[absent=1825533] state[empty=1825533] buckets[none=1825533] sources[not_implemented=1825533] quality[none]
- recent_ticks: presence[absent=80333, present=1745200] state[empty=80333, populated=1745200] buckets[many=1745200, none=80333] sources[none] quality[none]

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
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.0 | 0.0 | 0.0 | -0.0295 | None | 605.0962909460068 |
| SR_FLIP_RETEST | 4 | 4 | 0.0 | 0.0 | 0.0 | -0.0298 | None | 606.9050725698471 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 44932 | 67 | 23620 | 0.0 | 0.0 | None | 606.9050725698471 | 21312 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 19 | 1 | 18 | 0.0 | 0.0 | None | None | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `51`
- Gating Δ: `-5032`
- No-generation Δ: `1454412`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0162, "current_avg_pnl": -0.0295, "current_win_rate": 0.0, "previous_avg_pnl": -0.0457, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0298, "current_avg_pnl": -0.0298, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 61, "geometry_changed_delta": 0, "geometry_preserved_delta": 12646, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 606.91, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
