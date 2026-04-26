# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `12` sec (warning=False)
- Latest performance record age: `77773` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 126 | 126 | 110 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 117352 | 117350 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 117352 | 117226 | 126 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 117352 | 117352 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 117352 | 107422 | 9930 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 117352 | 117350 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 117352 | 117352 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 117352 | 117352 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 117352 | 117350 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 117352 | 117250 | 102 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 117352 | 109016 | 8336 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 117352 | 114522 | 2830 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 117352 | 117256 | 96 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 117352 | 117350 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 117352 | 117352 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 9930 | 9930 | 7667 | 63 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 2830 | 2830 | 2226 | 1 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 102 | 102 | 50 | 2 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 8336 | 8336 | 4595 | 86 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 96 | 96 | 91 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=101972, volume_spike_missing=11645, basic_filters_failed=3099
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=104232, ema_alignment_reject=4098, sweeps_not_detected=3517
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=104232, cvd_divergence_failed=10243, basic_filters_failed=2755
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=46951, basic_filters_failed=34118, reclaim_hold_failed=14721
- EVAL::FUNDING_EXTREME: regime_blocked=101972, funding_not_extreme=10827, basic_filters_failed=3099
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=79619, basic_filters_failed=34199, cvd_divergence_failed=3531
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=117352
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=104232, breakout_not_found=4541, ema_alignment_reject=4098
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=43056, basic_filters_failed=31363, compression_not_detected=23986
- EVAL::SR_FLIP_RETEST: basic_filters_failed=33773, reclaim_hold_failed=27129, flip_close_not_confirmed=26440
- EVAL::STANDARD: momentum_reject=47736, basic_filters_failed=25801, adx_reject=21327
- EVAL::TREND_PULLBACK: regime_blocked=104232, ema_alignment_reject=4052, basic_filters_failed=2740
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=101972, volume_spike_missing=11646, basic_filters_failed=3099
- EVAL::WHALE_MOMENTUM: regime_blocked=101972, momentum_reject=15380

## Dependency readiness
- cvd: presence[absent=9839, present=107513] state[empty=9839, populated=107513] buckets[few=633, many=101764, none=9839, some=5116] sources[none] quality[none]
- funding_rate: presence[absent=1458, present=115894] state[empty=1458, populated=115894] buckets[few=115894, none=1458] sources[none] quality[none]
- liquidation_clusters: presence[absent=65784, present=51568] state[empty=65784, populated=51568] buckets[few=39012, none=65784, some=12556] sources[none] quality[none]
- oi_snapshot: presence[absent=795, present=116557] state[empty=795, populated=116557] buckets[many=116557, none=795] sources[none] quality[none]
- order_book: presence[absent=39922, present=77430] state[populated=77430, unavailable=39922] buckets[few=77430, none=39922] sources[book_ticker=77430, unavailable=39922] quality[none=39922, top_of_book_only=77430]
- orderblocks: presence[absent=117352] state[empty=117352] buckets[none=117352] sources[not_implemented=117352] quality[none]
- recent_ticks: presence[absent=3957, present=113395] state[empty=3957, populated=113395] buckets[many=113395, none=3957] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.1139209270477295` sec
- Median create→first breach: `None` sec
- Median create→terminal: `757.9481258392334` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 7 | 7 | 0.0 | 0.0 | 0.0 | 0.2769 | None | 757.9481258392334 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 8336 | 86 | 4595 | 0.0 | 0.0 | None | 757.9481258392334 | 3741 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 96 | 0 | 91 | 0.0 | 0.0 | None | None | 5 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `154`
- Gating Δ: `14747`
- No-generation Δ: `1621500`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": 0.314, "current_avg_pnl": 0.2769, "current_win_rate": 0.0, "previous_avg_pnl": -0.0371, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 86, "geometry_changed_delta": 0, "geometry_preserved_delta": 3741, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -45.62, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -629.84, "median_terminal_delta_sec": -631.06, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **TREND_PULLBACK_EMA**
- Suggested next investigation target: **SR_FLIP_RETEST**
