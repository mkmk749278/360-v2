# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `25` sec (warning=False)
- Latest performance record age: `48132` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 53 | 53 | 37 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 49440 | 49440 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 49440 | 49387 | 53 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 49440 | 49440 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 49440 | 45471 | 3969 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 49440 | 49438 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 49440 | 49440 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 49440 | 49440 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 49440 | 49440 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 49440 | 49399 | 41 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 49440 | 45765 | 3675 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 49440 | 48064 | 1376 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 49440 | 49386 | 54 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 49440 | 49438 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 49440 | 49440 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3969 | 3969 | 2981 | 20 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 1376 | 1376 | 983 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 41 | 41 | 17 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 3675 | 3675 | 2030 | 32 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 54 | 54 | 53 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=40206, volume_spike_missing=6904, basic_filters_failed=1933
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=40862, ema_alignment_reject=2606, sweeps_not_detected=2417
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=40862, cvd_divergence_failed=6616, basic_filters_failed=1898
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=19255, basic_filters_failed=16340, reclaim_hold_failed=5391
- EVAL::FUNDING_EXTREME: regime_blocked=40206, funding_not_extreme=6434, basic_filters_failed=1933
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=31371, basic_filters_failed=16375, cvd_divergence_failed=1691
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=49440
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=40862, breakout_not_found=3038, ema_alignment_reject=2606
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=16319, basic_filters_failed=14442, regime_blocked=9234
- EVAL::SR_FLIP_RETEST: basic_filters_failed=15995, flip_close_not_confirmed=10807, reclaim_hold_failed=10065
- EVAL::STANDARD: momentum_reject=18001, basic_filters_failed=12265, sweeps_not_detected=8487
- EVAL::TREND_PULLBACK: regime_blocked=40862, ema_alignment_reject=2560, basic_filters_failed=1883
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=40206, volume_spike_missing=6904, basic_filters_failed=1933
- EVAL::WHALE_MOMENTUM: regime_blocked=40206, momentum_reject=9234

## Dependency readiness
- cvd: presence[absent=9089, present=40351] state[empty=9089, populated=40351] buckets[few=633, many=34602, none=9089, some=5116] sources[none] quality[none]
- funding_rate: presence[absent=708, present=48732] state[empty=708, populated=48732] buckets[few=48732, none=708] sources[none] quality[none]
- liquidation_clusters: presence[absent=26486, present=22954] state[empty=26486, populated=22954] buckets[few=17161, none=26486, some=5793] sources[none] quality[none]
- oi_snapshot: presence[absent=45, present=49395] state[empty=45, populated=49395] buckets[many=49395, none=45] sources[none] quality[none]
- order_book: presence[absent=12986, present=36454] state[populated=36454, unavailable=12986] buckets[few=36454, none=12986] sources[book_ticker=36454, unavailable=12986] quality[none=12986, top_of_book_only=36454]
- orderblocks: presence[absent=49440] state[empty=49440] buckets[none=49440] sources[not_implemented=49440] quality[none]
- recent_ticks: presence[absent=1552, present=47888] state[empty=1552, populated=47888] buckets[many=47888, none=1552] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.4257819652557373` sec
- Median create→first breach: `629.8351180553436` sec
- Median create→terminal: `757.9481258392334` sec
- Median first breach→terminal: `1.2232398986816406` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.4561 | None | 612.6194648742676 |
| SR_FLIP_RETEST | 9 | 9 | 0.0 | 0.0 | 0.0 | 0.2083 | None | 796.9779269695282 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | -0.7009 | 629.8351180553436 | 631.0583579540253 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 3675 | 32 | 2030 | 0.0 | 0.0 | None | 796.9779269695282 | 1645 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 54 | 0 | 53 | 0.0 | 100.0 | 629.8351180553436 | 631.0583579540253 | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `54`
- Gating Δ: `6105`
- No-generation Δ: `682988`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": 0.2468, "current_avg_pnl": 0.2083, "current_win_rate": 0.0, "previous_avg_pnl": -0.0385, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 32, "geometry_changed_delta": 0, "geometry_preserved_delta": 1645, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -34.53, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 629.84, "median_terminal_delta_sec": 631.06, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
