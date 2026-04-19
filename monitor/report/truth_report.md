# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, TREND_PULLBACK_EMA, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `15` sec (warning=False)
- Latest performance record age: `27040` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1312 | 1312 | 1157 | 7 | low-sample |
| EVAL::BREAKDOWN_SHORT | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 650476 | 649164 | 1312 | 0 | 0 | 0 | low-sample |
| EVAL::DIVERGENCE_CONTINUATION | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| EVAL::FAILED_AUCTION_RECLAIM | 650476 | 565560 | 84916 | 0 | 0 | 0 | low-sample |
| EVAL::FUNDING_EXTREME | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| EVAL::LIQUIDATION_REVERSAL | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| EVAL::OPENING_RANGE_BREAKOUT | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 650476 | 650430 | 46 | 0 | 0 | 0 | low-sample |
| EVAL::QUIET_COMPRESSION_BREAK | 650476 | 649773 | 703 | 0 | 0 | 0 | low-sample |
| EVAL::SR_FLIP_RETEST | 650476 | 639838 | 10638 | 0 | 0 | 0 | low-sample |
| EVAL::STANDARD | 650476 | 633155 | 17321 | 0 | 0 | 0 | low-sample |
| EVAL::TREND_PULLBACK | 650476 | 649451 | 1025 | 0 | 0 | 0 | low-sample |
| EVAL::VOLUME_SURGE_BREAKOUT | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| EVAL::WHALE_MOMENTUM | 650476 | 650476 | 0 | 0 | 0 | 0 | non-generating |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 84916 | 84916 | 84740 | 4 | low-sample |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 17321 | 17321 | 14175 | 2 | low-sample |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 46 | 46 | 45 | 1 | low-sample |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 703 | 703 | 703 | 0 | low-sample |
| SR_FLIP_RETEST | 0 | 0 | 10638 | 10638 | 9278 | 19 | active-low-quality |
| TREND_PULLBACK_EMA | 0 | 0 | 1025 | 1025 | 731 | 15 | active-low-quality |

## Lifecycle truth summary
- Median create→dispatch: `1.5443105697631836` sec
- Median create→first breach: `183.88034391403198` sec
- Median create→terminal: `186.06871700286865` sec
- Median first breach→terminal: `0.7272298336029053` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 13, "pct": 92.9}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 2 | 2 | 0.0 | 50.0 | 0.0 | -0.459 | 180.69527101516724 | 401.8299344778061 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | -0.7362 | 186.36427402496338 | 187.31129384040833 |
| SR_FLIP_RETEST | 3 | 3 | 0.0 | 100.0 | 0.0 | -0.4263 | 181.05250597000122 | 184.48625493049622 |
| TREND_PULLBACK_EMA | 8 | 8 | 0.0 | 100.0 | 0.0 | -0.297 | 184.07737946510315 | 185.82900309562683 |

## Window-over-window comparison
- Path emissions Δ: `48`
- Gating Δ: `110829`
- No-generation Δ: `8990703`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.2449, "current_avg_pnl": -0.4263, "current_win_rate": 0.0, "previous_avg_pnl": -0.1814, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.4241, "current_avg_pnl": -0.297, "current_win_rate": 0.0, "previous_avg_pnl": 0.1271, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **QUIET_COMPRESSION_BREAK**
- Suggested next investigation target: **SR_FLIP_RETEST**
