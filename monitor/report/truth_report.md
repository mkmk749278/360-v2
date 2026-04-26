# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::TREND_PULLBACK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `50` sec (warning=False)
- Latest performance record age: `32263` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 37054 | 37052 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 37054 | 37054 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 37054 | 35591 | 1463 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 37054 | 37052 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 37054 | 37054 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (basic_filters_failed) |
| EVAL::SR_FLIP_RETEST | 37054 | 34775 | 2279 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 37054 | 36300 | 754 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 37054 | 37054 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1463 | 1463 | 1346 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 754 | 754 | 754 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 2279 | 2279 | 1719 | 4 | active-low-quality (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=25769, volume_spike_missing=6941, basic_filters_failed=2979
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=31285, basic_filters_failed=1559, sweeps_not_detected=1516
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=31285, missing_cvd=3383, basic_filters_failed=1559
- EVAL::FAILED_AUCTION_RECLAIM: basic_filters_failed=13774, reclaim_hold_failed=6880, auction_not_detected=5534
- EVAL::FUNDING_EXTREME: regime_blocked=25769, funding_not_extreme=7347, basic_filters_failed=2949
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=19501, basic_filters_failed=15194, missing_cvd=1244
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=37054
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=31285, basic_filters_failed=1559, breakout_not_found=1559
- EVAL::QUIET_COMPRESSION_BREAK: basic_filters_failed=12215, regime_blocked=11271, breakout_not_detected=8304
- EVAL::SR_FLIP_RETEST: basic_filters_failed=13774, reclaim_hold_failed=5756, regime_blocked=5502
- EVAL::STANDARD: momentum_reject=12995, basic_filters_failed=11592, adx_reject=7514
- EVAL::TREND_PULLBACK: regime_blocked=31285, basic_filters_failed=1559, ema_alignment_reject=1325
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=25769, volume_spike_missing=6941, basic_filters_failed=2979
- EVAL::WHALE_MOMENTUM: regime_blocked=25769, momentum_reject=11285

## Dependency readiness
- cvd: presence[absent=35073, present=1981] state[empty=35073, populated=1981] buckets[few=318, many=1419, none=35073, some=244] sources[none] quality[none]
- funding_rate: presence[absent=585, present=36469] state[empty=585, populated=36469] buckets[few=36469, none=585] sources[none] quality[none]
- liquidation_clusters: presence[absent=37054] state[empty=37054] buckets[none=37054] sources[none] quality[none]
- oi_snapshot: presence[present=37054] state[populated=37054] buckets[many=37054] sources[none] quality[none]
- order_book: presence[absent=2278, present=34776] state[populated=34776, unavailable=2278] buckets[few=34776, none=2278] sources[book_ticker=34776, unavailable=2278] quality[none=2278, top_of_book_only=34776]
- orderblocks: presence[absent=37054] state[empty=37054] buckets[none=37054] sources[not_implemented=37054] quality[none]
- recent_ticks: presence[absent=1098, present=35956] state[empty=1098, populated=35956] buckets[many=35956, none=1098] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.458193063735962` sec
- Median create→first breach: `629.8351180553436` sec
- Median create→terminal: `766.2268264293671` sec
- Median first breach→terminal: `1.2232398986816406` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.4561 | None | 612.6194648742676 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0319 | None | 652.1576788425446 |
| SR_FLIP_RETEST | 17 | 17 | 0.0 | 0.0 | 0.0 | 0.0922 | None | 796.9779269695282 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | -0.7009 | 629.8351180553436 | 631.0583579540253 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 2279 | 4 | 1719 | 0.0 | 0.0 | None | 796.9779269695282 | 560 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 100.0 | 629.8351180553436 | 631.0583579540253 | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `4`
- Gating Δ: `3823`
- No-generation Δ: `514256`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": 0.0922, "current_avg_pnl": 0.0922, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 560, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 796.98, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 629.84, "median_terminal_delta_sec": 631.06, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FAILED_AUCTION_RECLAIM**
- Suggested next investigation target: **SR_FLIP_RETEST**
