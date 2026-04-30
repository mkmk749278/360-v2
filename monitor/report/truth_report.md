# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::STANDARD, EVAL::TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::STANDARD**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `16211` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| EVAL::BREAKDOWN_SHORT | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (volume_spike_missing) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 18423 | 18422 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 18423 | 18328 | 95 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 18423 | 18422 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| EVAL::TREND_PULLBACK | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (volume_spike_missing) |
| EVAL::WHALE_MOMENTUM | 18423 | 18423 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 95 | 95 | 95 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: volume_spike_missing=11557, basic_filters_failed=3558, regime_blocked=3297
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=18420, basic_filters_failed=1, sweeps_not_detected=1
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=18420, basic_filters_failed=1, cvd_divergence_failed=1
- EVAL::FAILED_AUCTION_RECLAIM: regime_blocked=15123, auction_not_detected=2156, basic_filters_failed=540
- EVAL::FUNDING_EXTREME: funding_not_extreme=11763, basic_filters_failed=3879, missing_funding_rate=1825
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=14151, basic_filters_failed=4097, cvd_divergence_failed=175
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=18423
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=18420, basic_filters_failed=1, breakout_not_found=1
- EVAL::QUIET_COMPRESSION_BREAK: regime_blocked=15126, breakout_not_detected=2162, basic_filters_failed=539
- EVAL::SR_FLIP_RETEST: regime_blocked=15123, flip_close_not_confirmed=1562, wick_quality_failed=600
- EVAL::STANDARD: momentum_reject=7330, basic_filters_failed=3666, sweeps_not_detected=3510
- EVAL::TREND_PULLBACK: regime_blocked=18420, basic_filters_failed=1, body_conviction_fail=1
- EVAL::VOLUME_SURGE_BREAKOUT: volume_spike_missing=11557, basic_filters_failed=3558, regime_blocked=3297
- EVAL::WHALE_MOMENTUM: momentum_reject=15126, regime_blocked=3297

## Dependency readiness
- cvd: presence[absent=1872, present=16551] state[empty=1872, populated=16551] buckets[many=4353, none=1872, some=12198] sources[none] quality[none]
- funding_rate: presence[absent=1825, present=16598] state[empty=1825, populated=16598] buckets[few=16598, none=1825] sources[none] quality[none]
- liquidation_clusters: presence[absent=18423] state[empty=18423] buckets[none=18423] sources[none] quality[none]
- oi_snapshot: presence[absent=34, present=18389] state[empty=34, populated=18389] buckets[many=18389, none=34] sources[none] quality[none]
- order_book: presence[absent=1416, present=17007] state[populated=17007, unavailable=1416] buckets[few=17007, none=1416] sources[book_ticker=17007, unavailable=1416] quality[none=1416, top_of_book_only=17007]
- orderblocks: presence[absent=18423] state[empty=18423] buckets[none=18423] sources[not_implemented=18423] quality[none]
- recent_ticks: presence[absent=406, present=18017] state[empty=406, populated=18017] buckets[many=18017, none=406] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.074831962585449` sec
- Median create→first breach: `None` sec
- Median create→terminal: `608.9487729072571` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 0.0 | 0.0 | -0.0457 | None | 608.9487729072571 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1 | 0 | 0 | 0.0 | 0.0 | None | None | 1 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `95`
- No-generation Δ: `257825`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0404, "current_avg_pnl": -0.0457, "current_win_rate": 0.0, "previous_avg_pnl": -0.0861, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::STANDARD**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **EVAL::STANDARD**
