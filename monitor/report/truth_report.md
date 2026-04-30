# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: QUIET_COMPRESSION_BREAK, EVAL::TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **QUIET_COMPRESSION_BREAK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `29466` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 12 | 12 | 10 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 3 | 3 | 1 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 230 | 230 | 9 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1858035 | 1858023 | 12 | 0 | 0 | 0 | low-sample (volume_spike_missing) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1858035 | 1858032 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1858035 | 1857805 | 230 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1858035 | 1846669 | 11366 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1858035 | 1852592 | 5443 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1858035 | 1858035 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1858035 | 1858035 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1858035 | 1858035 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1858035 | 1857774 | 261 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1858035 | 1848604 | 9431 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1858035 | 1854086 | 3949 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1858035 | 1858035 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1858035 | 1858035 | 0 | 0 | 0 | 0 | non-generating (volume_spike_missing) |
| EVAL::WHALE_MOMENTUM | 1858035 | 1858035 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 11366 | 11366 | 4667 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 5443 | 5443 | 5443 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 3949 | 3949 | 3896 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 261 | 261 | 200 | 8 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 9431 | 9431 | 6018 | 13 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1858023): volume_spike_missing=1024048, basic_filters_failed=341996, regime_blocked=299220, breakout_not_found=147492, retest_proximity_failed=45265, ema_alignment_reject=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1858032): regime_blocked=1820723, ema_alignment_reject=18567, sweeps_not_detected=9904, basic_filters_failed=5532, adx_reject=2713, momentum_reject=581, reclaim_confirmation_failed=11, rsi_reject=1
- **EVAL::DIVERGENCE_CONTINUATION** (total=1857805): regime_blocked=1820723, cvd_divergence_failed=21826, basic_filters_failed=5532, ema_alignment_reject=5174, retest_proximity_failed=4274, missing_cvd=276
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1846669): regime_blocked=1521491, auction_not_detected=195569, reclaim_hold_failed=53091, basic_filters_failed=38073, adx_reject=18791, tail_too_small=18671, rsi_reject=983
- **EVAL::FUNDING_EXTREME** (total=1852592): funding_not_extreme=1308293, basic_filters_failed=360418, missing_funding_rate=118714, ema_alignment_reject=34574, rsi_reject=30522, cvd_divergence_failed=69, momentum_reject=2
- **EVAL::LIQUIDATION_REVERSAL** (total=1858035): cascade_threshold_not_met=1458406, basic_filters_failed=374535, cvd_divergence_failed=25094
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1858035): regime_blocked=1542720, feature_disabled=315315
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1858035): regime_blocked=1820723, ema_alignment_reject=18567, breakout_not_found=10500, basic_filters_failed=5532, adx_reject=2713
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1857774): regime_blocked=1558803, breakout_not_detected=134374, compression_not_detected=60265, macd_reject=34775, basic_filters_failed=32541, volume_reject=27181, rsi_reject=8770, missing_fvg_or_orderblock=1065
- **EVAL::SR_FLIP_RETEST** (total=1848604): regime_blocked=1521491, flip_close_not_confirmed=142727, retest_out_of_zone=78444, basic_filters_failed=37810, reclaim_hold_failed=37491, wick_quality_failed=15603, rsi_reject=11395, missing_fvg_or_orderblock=2451, ema_alignment_reject=828, insufficient_candles=364
- **EVAL::STANDARD** (total=1854086): momentum_reject=768823, basic_filters_failed=313838, sweeps_not_detected=300580, adx_reject=236102, ema_alignment_reject=185056, insufficient_candles=26063, rsi_reject=22104, macd_reject=1115, invalid_sl_geometry=405
- **EVAL::TREND_PULLBACK** (total=1858035): regime_blocked=1820723, ema_alignment_reject=18567, ema_not_tested_prev=6333, basic_filters_failed=5532, rsi_reject=4381, no_ema_reclaim_close=1311, body_conviction_fail=1170, prev_already_below_emas=6, prev_already_above_emas=5, momentum_flat=4, ema21_not_tagged=2, no_prev_high_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1858035): volume_spike_missing=932274, basic_filters_failed=341996, regime_blocked=299220, retest_proximity_failed=142583, breakout_not_found=141959, ema_alignment_reject=3
- **EVAL::WHALE_MOMENTUM** (total=1858035): momentum_reject=1558815, regime_blocked=299220

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 179974 | 83.9% |
| QUIET | 34583 | 16.1% |
| TRENDING_UP | 43 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **524**
- Average confidence gap to threshold: **18.81** (samples=524) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XAGUSDT=84, XAUUSDT=66, DOGEUSDT=62, XRPUSDT=57, CLUSDT=53, ETHUSDT=39, SOLUSDT=34, BTCUSDT=33, BNBUSDT=32, TRXUSDT=13

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 1 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | watchlist_tier_keep | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 213 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 5139 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 230 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 47 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 53 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 5 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 3 |
| SR_FLIP_RETEST | filtered | min_confidence | 1444 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 247 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 140 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 67.35 | 80.00 | 12.65 | 20.55 | 20.00 | 18.50 | 0.00 | 3.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 1 | 66.00 | 80.00 | 14.00 | 24.00 | 20.00 | 15.20 | 0.00 | 6.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 60.70 | 50.00 | -10.70 | 20.10 | 20.00 | 15.20 | 0.00 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 213 | 46.27 | 80.00 | 33.73 | 20.80 | 19.90 | 20.00 | 0.37 | 4.80 |
| DIVERGENCE_CONTINUATION | kept | 3 | 60.57 | 60.00 | -0.57 | 21.07 | 19.93 | 20.00 | 1.67 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 5369 | 44.46 | 79.36 | 34.90 | 22.92 | 18.09 | 12.80 | 1.11 | 6.08 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 52.56 | 65.31 | 12.75 | 21.50 | 19.88 | 13.80 | 2.42 | 0.45 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 62.70 | 50.00 | -12.70 | 20.10 | 20.00 | 13.80 | 2.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 53 | 70.65 | 80.00 | 9.35 | 20.22 | 19.78 | 14.31 | 0.00 | 1.83 |
| QUIET_COMPRESSION_BREAK | kept | 8 | 67.69 | 61.25 | -6.44 | 21.56 | 18.84 | 14.20 | 0.00 | 14.45 |
| SR_FLIP_RETEST | filtered | 1691 | 52.25 | 77.81 | 25.56 | 20.28 | 19.99 | 14.33 | 0.71 | 7.03 |
| SR_FLIP_RETEST | kept | 140 | 64.16 | 50.00 | -14.16 | 19.56 | 19.99 | 13.80 | 1.00 | 0.63 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8179438`
- `Path funnel` emissions: `311`
- `Regime distribution` emissions: `29`
- `QUIET_SCALP_BLOCK` events: `585`
- `confidence_gate` events: `7530`

## Dependency readiness
- cvd: presence[absent=132462, present=1725573] state[empty=132462, populated=1725573] buckets[many=396970, none=132462, some=1328603] sources[none] quality[none]
- funding_rate: presence[absent=118714, present=1739321] state[empty=118714, populated=1739321] buckets[few=1739321, none=118714] sources[none] quality[none]
- liquidation_clusters: presence[absent=1858035] state[empty=1858035] buckets[none=1858035] sources[none] quality[none]
- oi_snapshot: presence[absent=27388, present=1830647] state[empty=27388, populated=1830647] buckets[few=652, many=1826518, none=27388, some=3477] sources[none] quality[none]
- order_book: presence[absent=146532, present=1711503] state[populated=1711503, unavailable=146532] buckets[few=1711503, none=146532] sources[book_ticker=1711503, unavailable=146532] quality[none=146532, top_of_book_only=1711503]
- orderblocks: presence[absent=1858035] state[empty=1858035] buckets[none=1858035] sources[not_implemented=1858035] quality[none]
- recent_ticks: presence[absent=50814, present=1807221] state[empty=50814, populated=1807221] buckets[many=1807221, none=50814] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.9833545684814453` sec
- Median create→first breach: `None` sec
- Median create→terminal: `609.6404575109482` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.2838 | None | 610.3321421146393 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 0.0 | 0.0 | -0.0457 | None | 608.9487729072571 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 9431 | 13 | 6018 | 0.0 | 0.0 | None | None | 3413 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-30`
- Gating Δ: `-264646`
- No-generation Δ: `4335869`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0404, "current_avg_pnl": -0.0457, "current_win_rate": 0.0, "previous_avg_pnl": -0.0861, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 13, "geometry_changed_delta": 0, "geometry_preserved_delta": -13022, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **QUIET_COMPRESSION_BREAK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **QUIET_COMPRESSION_BREAK**
