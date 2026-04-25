# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `38` sec (warning=False)
- Latest performance record age: `2234` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 30523 | 30521 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 30523 | 30522 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 30523 | 30523 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 30523 | 28258 | 2265 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 30523 | 30523 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 30523 | 30523 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 30523 | 30523 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 30523 | 30523 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 30523 | 30494 | 29 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 30523 | 28297 | 2226 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 30523 | 30030 | 493 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 30523 | 30520 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 30523 | 30523 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 30523 | 30523 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2265 | 2265 | 1334 | 6 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 493 | 493 | 395 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 29 | 29 | 3 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 2226 | 2226 | 1164 | 9 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=26684, volume_spike_missing=2543, basic_filters_failed=1167
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=30338, ema_alignment_reject=64, sweeps_not_detected=54
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=30338, cvd_divergence_failed=149, cvd_insufficient=19
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=11172, basic_filters_failed=8734, reclaim_hold_failed=3494
- EVAL::FUNDING_EXTREME: regime_blocked=26684, funding_not_extreme=2613, basic_filters_failed=1165
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=20609, basic_filters_failed=9291, cvd_divergence_failed=611
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=30523
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=30338, breakout_not_found=69, ema_alignment_reject=64
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=12016, basic_filters_failed=8728, compression_not_detected=5517
- EVAL::SR_FLIP_RETEST: basic_filters_failed=8734, reclaim_hold_failed=6631, flip_close_not_confirmed=6361
- EVAL::STANDARD: momentum_reject=10929, basic_filters_failed=8387, adx_reject=5687
- EVAL::TREND_PULLBACK: regime_blocked=30338, ema_alignment_reject=64, no_ema_reclaim_close=38
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=26684, volume_spike_missing=2558, basic_filters_failed=1167
- EVAL::WHALE_MOMENTUM: regime_blocked=26684, momentum_reject=3839

## Dependency readiness
- cvd: presence[absent=4460, present=26063] state[empty=4460, populated=26063] buckets[few=592, many=19582, none=4460, some=5889] sources[none] quality[none]
- funding_rate: presence[absent=388, present=30135] state[empty=388, populated=30135] buckets[few=30135, none=388] sources[none] quality[none]
- liquidation_clusters: presence[absent=19740, present=10783] state[empty=19740, populated=10783] buckets[few=7736, none=19740, some=3047] sources[none] quality[none]
- oi_snapshot: presence[absent=48, present=30475] state[empty=48, populated=30475] buckets[many=30475, none=48] sources[none] quality[none]
- order_book: presence[absent=8443, present=22080] state[populated=22080, unavailable=8443] buckets[few=22080, none=8443] sources[book_ticker=22080, unavailable=8443] quality[none=8443, top_of_book_only=22080]
- orderblocks: presence[absent=30523] state[empty=30523] buckets[none=30523] sources[not_implemented=30523] quality[none]
- recent_ticks: presence[present=30523] state[populated=30523] buckets[many=30523] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.3113054037094116` sec
- Median create→first breach: `None` sec
- Median create→terminal: `909.7674354314804` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0319 | None | 652.1576788425446 |
| SR_FLIP_RETEST | 5 | 5 | 0.0 | 0.0 | 0.0 | -0.0833 | None | 931.0235638618469 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 2226 | 9 | 1164 | 0.0 | 0.0 | None | 931.0235638618469 | 1062 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3 | 0 | 3 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `16`
- Gating Δ: `2902`
- No-generation Δ: `422303`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.0833, "current_avg_pnl": -0.0833, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": 1062, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 931.02, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **QUIET_COMPRESSION_BREAK**
- Suggested next investigation target: **SR_FLIP_RETEST**
