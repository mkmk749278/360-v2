# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `3993` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Evaluator no-signal reasons

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `6.18731153011322` sec
- Median create→first breach: `184.27309393882751` sec
- Median create→terminal: `196.46404218673706` sec
- Median first breach→terminal: `0.7329949140548706` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 15, "pct": 68.2}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 6 | 6 | 0.0 | 50.0 | 0.0 | 0.1696 | 182.84176111221313 | 402.55582654476166 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | -1.296 | 188.029639005661 | 188.30536484718323 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.7408 | None | 602.5395729541779 |
| SR_FLIP_RETEST | 8 | 8 | 0.0 | 75.0 | 0.0 | -0.4748 | 185.3577799797058 | 189.48564898967743 |
| TREND_PULLBACK_EMA | 6 | 6 | 0.0 | 83.3 | 0.0 | -0.2282 | 184.21151995658875 | 194.52683448791504 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 75.0 | 185.3577799797058 | 189.48564898967743 | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 83.3 | 184.21151995658875 | 194.52683448791504 | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.3676, "current_avg_pnl": 0.1696, "current_win_rate": 0.0, "previous_avg_pnl": 1.5372, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.5135, "current_avg_pnl": -0.4748, "current_win_rate": 0.0, "previous_avg_pnl": 0.0387, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.1335, "current_avg_pnl": -0.2282, "current_win_rate": 0.0, "previous_avg_pnl": -0.0947, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2.13, "median_terminal_delta_sec": -443.41, "sl_rate_delta": 37.5, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -0.28, "median_terminal_delta_sec": 0.86, "sl_rate_delta": 5.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
