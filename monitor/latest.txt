# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `45` sec (warning=False)
- Latest performance record age: `None` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 6575 | 6570 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 6575 | 6006 | 569 | 0 | 0 | 0 | low-sample (reclaim_hold_failed) |
| EVAL::FUNDING_EXTREME | 6575 | 6575 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 6575 | 6572 | 3 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 6575 | 6322 | 253 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 6575 | 6196 | 379 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 6575 | 6572 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 6575 | 6575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 569 | 569 | 356 | 7 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 379 | 379 | 275 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 253 | 253 | 150 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=6149, volume_spike_missing=396, basic_filters_failed=17
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=6200, ema_alignment_reject=144, adx_reject=97
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=6200, cvd_divergence_failed=315, cvd_insufficient=46
- EVAL::FAILED_AUCTION_RECLAIM: reclaim_hold_failed=2255, auction_not_detected=1776, basic_filters_failed=1060
- EVAL::FUNDING_EXTREME: regime_blocked=6149, funding_not_extreme=364, missing_funding_rate=27
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=5252, basic_filters_failed=1063, cvd_divergence_failed=256
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=6575
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=6200, ema_alignment_reject=144, breakout_not_found=120
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=2669, compression_not_detected=1925, basic_filters_failed=1046
- EVAL::SR_FLIP_RETEST: flip_close_not_confirmed=3927, basic_filters_failed=1060, reclaim_hold_failed=715
- EVAL::STANDARD: momentum_reject=3490, basic_filters_failed=1230, adx_reject=884
- EVAL::TREND_PULLBACK: regime_blocked=6200, ema_alignment_reject=144, body_conviction_fail=70
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=6149, volume_spike_missing=394, basic_filters_failed=17
- EVAL::WHALE_MOMENTUM: regime_blocked=6149, momentum_reject=426

## Dependency readiness
- cvd: presence[present=6575] state[populated=6575] buckets[few=259, many=3182, some=3134] sources[none] quality[none]
- funding_rate: presence[absent=710, present=5865] state[empty=710, populated=5865] buckets[few=5865, none=710] sources[none] quality[none]
- liquidation_clusters: presence[absent=3608, present=2967] state[empty=3608, populated=2967] buckets[few=2385, none=3608, some=582] sources[none] quality[none]
- oi_snapshot: presence[absent=169, present=6406] state[empty=169, populated=6406] buckets[many=6406, none=169] sources[none] quality[none]
- order_book: presence[absent=3507, present=3068] state[populated=3068, unavailable=3507] buckets[few=3068, none=3507] sources[book_ticker=3068, unavailable=3507] quality[none=3507, top_of_book_only=3068]
- orderblocks: presence[absent=6575] state[empty=6575] buckets[none=6575] sources[not_implemented=6575] quality[none]
- recent_ticks: presence[absent=765, present=5810] state[empty=765, populated=5810] buckets[many=5810, none=765] sources[none] quality[none]

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
| SR_FLIP_RETEST | 0 | 253 | 2 | 150 | 0.0 | 0.0 | None | None | 103 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3 | 0 | 3 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `9`
- Gating Δ: `792`
- No-generation Δ: `90838`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 103, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
