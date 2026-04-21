# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `None` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| EVAL::BREAKDOWN_SHORT | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 6603 | 5960 | 643 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::FUNDING_EXTREME | 6603 | 6603 | 0 | 0 | 0 | 0 | dependency-missing (none) |
| EVAL::LIQUIDATION_REVERSAL | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (none) |
| EVAL::SR_FLIP_RETEST | 6603 | 6559 | 44 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 6603 | 6371 | 232 | 0 | 0 | 0 | low-sample (none) |
| EVAL::TREND_PULLBACK | 6603 | 6600 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 6603 | 6603 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 643 | 643 | 643 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 232 | 232 | 225 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 44 | 44 | 39 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=5925, volume_spike_missing=622, basic_filters_failed=56
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=6568, sweeps_not_detected=12, ema_alignment_reject=12
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=6568, cvd_insufficient=35
- EVAL::FAILED_AUCTION_RECLAIM: adx_reject=2299, auction_not_detected=1669, basic_filters_failed=1078
- EVAL::FUNDING_EXTREME: none=5925, funding_not_extreme=605, basic_filters_failed=54
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=5366, basic_filters_failed=1134, cvd_divergence_failed=75
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=6603
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=6568, breakout_not_found=13, ema_alignment_reject=12
- EVAL::QUIET_COMPRESSION_BREAK: none=6603
- EVAL::SR_FLIP_RETEST: flip_close_not_confirmed=4306, basic_filters_failed=1049, regime_blocked=643
- EVAL::STANDARD: none=6371
- EVAL::TREND_PULLBACK: regime_blocked=6568, ema_alignment_reject=12, none=7
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=5925, volume_spike_missing=622, basic_filters_failed=56
- EVAL::WHALE_MOMENTUM: regime_blocked=5925, momentum_reject=678

## Dependency readiness
- cvd: presence[present=6603] state[empty=7, populated=6596] buckets[few=2552, none=7, some=4044] sources[none] quality[none]
- funding_rate: presence[present=6603] state[empty=2549, populated=4054] buckets[few=4054, none=2549] sources[none] quality[none]
- liquidation_clusters: presence[present=6603] state[empty=5347, populated=1256] buckets[few=952, none=5347, some=304] sources[none] quality[none]
- oi_snapshot: presence[present=6603] state[empty=2544, populated=4059] buckets[few=3970, none=2544, some=89] sources[none] quality[none]
- order_book: presence[absent=2718, present=3885] state[populated=3885, unavailable=2718] buckets[few=3885, none=2718] sources[book_ticker=3885, unavailable=2718] quality[none=2718, top_of_book_only=3885]
- orderblocks: presence[absent=6603] state[unavailable=6603] buckets[none=6603] sources[none] quality[none]
- recent_ticks: presence[present=6603] state[empty=2300, populated=4303] buckets[many=4303, none=2300] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `None` sec
- Median create→first breach: `None` sec
- Median create→terminal: `None` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 44 | 0 | 39 | 0.0 | 0.0 | None | None | 5 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3 | 0 | 3 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `910`
- No-generation Δ: `91520`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FAILED_AUCTION_RECLAIM**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
