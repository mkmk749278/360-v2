# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `58739` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 619 | 619 | 619 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 289723 | 289723 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 289723 | 289104 | 619 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 289723 | 289723 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 289723 | 244721 | 45002 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 289723 | 289723 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 289723 | 289723 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 289723 | 289723 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 289723 | 289723 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 289723 | 279426 | 10297 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 289723 | 267645 | 22078 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 289723 | 277206 | 12517 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 289723 | 289719 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 289723 | 289723 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 289723 | 289723 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 45002 | 45002 | 39282 | 5 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 12517 | 12517 | 11353 | 3 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 10297 | 10297 | 5235 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 22078 | 22078 | 15447 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=217529, volume_spike_missing=44384, basic_filters_failed=25144
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=279795, ema_alignment_reject=4650, basic_filters_failed=2943
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=279795, cvd_divergence_failed=6231, basic_filters_failed=2943
- EVAL::FAILED_AUCTION_RECLAIM: basic_filters_failed=103236, auction_not_detected=59197, tail_too_small=43407
- EVAL::FUNDING_EXTREME: funding_not_extreme=177217, basic_filters_failed=103231, cvd_divergence_failed=3691
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=186409, basic_filters_failed=103239, cvd_divergence_failed=75
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=289723
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=279795, ema_alignment_reject=4650, basic_filters_failed=2943
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=119453, basic_filters_failed=100293, compression_not_detected=29465
- EVAL::SR_FLIP_RETEST: basic_filters_failed=103236, reclaim_hold_failed=68821, retest_out_of_zone=37538
- EVAL::STANDARD: basic_filters_failed=105593, momentum_reject=104738, adx_reject=51439
- EVAL::TREND_PULLBACK: regime_blocked=279795, ema_alignment_reject=4650, basic_filters_failed=2943
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=217529, volume_spike_missing=44384, basic_filters_failed=25144
- EVAL::WHALE_MOMENTUM: regime_blocked=217529, momentum_reject=72194

## Dependency readiness
- cvd: presence[absent=25762, present=263961] state[empty=25762, populated=263961] buckets[many=263961, none=25762] sources[none] quality[none]
- funding_rate: presence[absent=49, present=289674] state[empty=49, populated=289674] buckets[few=289674, none=49] sources[none] quality[none]
- liquidation_clusters: presence[absent=289723] state[empty=289723] buckets[none=289723] sources[none] quality[none]
- oi_snapshot: presence[absent=49, present=289674] state[empty=49, populated=289674] buckets[few=140, many=289106, none=49, some=428] sources[none] quality[none]
- order_book: presence[absent=15567, present=274156] state[populated=274156, unavailable=15567] buckets[few=274156, none=15567] sources[book_ticker=274156, unavailable=15567] quality[none=15567, top_of_book_only=274156]
- orderblocks: presence[absent=289723] state[empty=289723] buckets[none=289723] sources[not_implemented=289723] quality[none]
- recent_ticks: presence[absent=24095, present=265628] state[empty=24095, populated=265628] buckets[many=265628, none=24095] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.910701036453247` sec
- Median create→first breach: `274.706326007843` sec
- Median create→terminal: `725.657634973526` sec
- Median first breach→terminal: `2.713870048522949` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.3787 | None | 725.657634973526 |
| SR_FLIP_RETEST | 2 | 2 | 0.0 | 50.0 | 0.0 | -0.4114 | 274.706326007843 | 522.9527995586395 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 22078 | 7 | 15447 | 0.0 | 50.0 | 274.706326007843 | 522.9527995586395 | 6631 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4 | 0 | 4 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `15`
- Gating Δ: `71940`
- No-generation Δ: `3965605`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.6126, "current_avg_pnl": -0.4114, "current_win_rate": 0.0, "previous_avg_pnl": 0.2012, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 7, "geometry_changed_delta": 0, "geometry_preserved_delta": 6631, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2681.53, "median_terminal_delta_sec": -656.69, "sl_rate_delta": 50.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **QUIET_COMPRESSION_BREAK**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
