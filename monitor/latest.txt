# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `46835` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| EVAL::BREAKDOWN_SHORT | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 461710 | 461710 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 461710 | 410544 | 51166 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 461710 | 460085 | 1625 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 461710 | 461710 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 461710 | 447612 | 14098 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 461710 | 429496 | 32214 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 461710 | 453062 | 8648 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 461710 | 461710 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 51166 | 51166 | 47564 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1625 | 1625 | 1625 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8648 | 8648 | 8416 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 14098 | 14098 | 385 | 14 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 32214 | 32214 | 25901 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=461031, volume_spike_missing=553, basic_filters_failed=97
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=461653, sweeps_not_detected=29, adx_reject=14
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=461653, missing_cvd=44, cvd_divergence_failed=7
- EVAL::FAILED_AUCTION_RECLAIM: basic_filters_failed=186590, auction_not_detected=112897, reclaim_hold_failed=61128
- EVAL::FUNDING_EXTREME: funding_not_extreme=271643, basic_filters_failed=186658, ema_alignment_reject=1313
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=273382, basic_filters_failed=186685, missing_cvd=1642
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=461710
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=461653, breakout_not_found=30, adx_reject=14
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=187467, basic_filters_failed=186584, compression_not_detected=38542
- EVAL::SR_FLIP_RETEST: basic_filters_failed=180878, reclaim_hold_failed=106359, retest_out_of_zone=52036
- EVAL::STANDARD: momentum_reject=168544, basic_filters_failed=123428, adx_reject=102207
- EVAL::TREND_PULLBACK: regime_blocked=461653, rsi_reject=16, body_conviction_fail=13
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=461031, volume_spike_missing=553, basic_filters_failed=97
- EVAL::WHALE_MOMENTUM: regime_blocked=461031, momentum_reject=679

## Dependency readiness
- cvd: presence[absent=389520, present=72190] state[empty=389520, populated=72190] buckets[many=72190, none=389520] sources[none] quality[none]
- funding_rate: presence[absent=49, present=461661] state[empty=49, populated=461661] buckets[few=461661, none=49] sources[none] quality[none]
- liquidation_clusters: presence[absent=461710] state[empty=461710] buckets[none=461710] sources[none] quality[none]
- oi_snapshot: presence[absent=48, present=461662] state[empty=48, populated=461662] buckets[few=253, many=459985, none=48, some=1424] sources[none] quality[none]
- order_book: presence[absent=26106, present=435604] state[populated=435604, unavailable=26106] buckets[few=435604, none=26106] sources[book_ticker=435604, unavailable=26106] quality[none=26106, top_of_book_only=435604]
- orderblocks: presence[absent=461710] state[empty=461710] buckets[none=461710] sources[not_implemented=461710] quality[none]
- recent_ticks: presence[absent=28571, present=433139] state[empty=28571, populated=433139] buckets[many=433139, none=28571] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.4005110263824463` sec
- Median create→first breach: `None` sec
- Median create→terminal: `1510.1236500740051` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0861 | None | 1510.1236500740051 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 32214 | 0 | 25901 | 0.0 | 0.0 | None | None | 6313 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `14`
- Gating Δ: `83891`
- No-generation Δ: `6356189`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 6313, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -768.49, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FAILED_AUCTION_RECLAIM**
- Suggested next investigation target: **EVAL::TREND_PULLBACK**
