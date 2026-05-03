# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `56112` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 143 | 143 | 139 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 42 | 42 | 42 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1588101 | 1588097 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1588101 | 1587958 | 143 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1588101 | 1588059 | 42 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1588101 | 1522672 | 65429 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1588101 | 1587545 | 556 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1588101 | 1588101 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1588101 | 1588101 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1588101 | 1588101 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1588101 | 1582756 | 5345 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1588101 | 1525279 | 62822 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1588101 | 1526781 | 61320 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1588101 | 1587957 | 144 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1588101 | 1588100 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1588101 | 1588101 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 65429 | 65429 | 57225 | 8 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 556 | 556 | 556 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 61320 | 61320 | 57900 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 5345 | 5345 | 5039 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 62822 | 62822 | 25650 | 83 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 144 | 144 | 6 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1588097): regime_blocked=719046, breakout_not_found=563889, basic_filters_failed=152679, retest_proximity_failed=144773, volume_spike_missing=7707, ema_alignment_reject=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1587958): regime_blocked=1263536, sweeps_not_detected=132202, ema_alignment_reject=101329, basic_filters_failed=85055, adx_reject=5465, momentum_reject=341, reclaim_confirmation_failed=29, rsi_reject=1
- **EVAL::DIVERGENCE_CONTINUATION** (total=1588059): regime_blocked=1263536, cvd_divergence_failed=181982, basic_filters_failed=85055, missing_cvd=20888, ema_alignment_reject=19774, retest_proximity_failed=16822, missing_fvg_or_orderblock=2
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1522672): regime_blocked=544490, auction_not_detected=435971, basic_filters_failed=371859, reclaim_hold_failed=94596, tail_too_small=75171, rsi_reject=585
- **EVAL::FUNDING_EXTREME** (total=1587545): funding_not_extreme=1124697, basic_filters_failed=438605, ema_alignment_reject=12823, missing_funding_rate=4094, momentum_reject=3747, rsi_reject=3331, cvd_divergence_failed=247, missing_fvg_or_orderblock=1
- **EVAL::LIQUIDATION_REVERSAL** (total=1588101): cascade_threshold_not_met=1112140, basic_filters_failed=439483, cvd_divergence_failed=36404, rsi_reject=74
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1588101): feature_disabled=1588101
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1588101): regime_blocked=1263536, breakout_not_found=132716, ema_alignment_reject=101329, basic_filters_failed=85055, adx_reject=5465
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1582756): regime_blocked=869055, basic_filters_failed=286804, breakout_not_detected=234335, compression_not_detected=150055, rsi_reject=28660, missing_fvg_or_orderblock=7080, macd_reject=6767
- **EVAL::SR_FLIP_RETEST** (total=1525279): regime_blocked=544490, basic_filters_failed=362555, retest_out_of_zone=309011, flip_close_not_confirmed=153159, reclaim_hold_failed=125063, insufficient_candles=13870, wick_quality_failed=7513, missing_fvg_or_orderblock=6300, rsi_reject=2360, ema_alignment_reject=958
- **EVAL::STANDARD** (total=1526781): momentum_reject=565667, basic_filters_failed=275711, adx_reject=257408, sweeps_not_detected=232108, ema_alignment_reject=137450, macd_reject=25571, insufficient_candles=20714, invalid_sl_geometry=11998, rsi_reject=154
- **EVAL::TREND_PULLBACK** (total=1587957): regime_blocked=1263536, ema_alignment_reject=101309, ema_not_tested_prev=101056, basic_filters_failed=79321, body_conviction_fail=17729, rsi_reject=10196, insufficient_candles=9534, no_ema_reclaim_close=3475, prev_already_below_emas=1669, no_prev_high_break=123, missing_fvg_or_orderblock=5, prev_already_above_emas=3, no_prev_low_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1588100): regime_blocked=719046, breakout_not_found=434595, retest_proximity_failed=263143, basic_filters_failed=152679, volume_spike_missing=18637
- **EVAL::WHALE_MOMENTUM** (total=1588101): momentum_reject=869055, regime_blocked=719046

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 987039 | 46.6% |
| VOLATILE | 713743 | 33.7% |
| TRENDING_UP | 347756 | 16.4% |
| TRENDING_DOWN | 67976 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **5914**
- Average confidence gap to threshold: **24.05** (samples=5914) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=1135, WLFIUSDT=502, DASHUSDT=466, DOTUSDT=444, ONDOUSDT=439, ZEREBROUSDT=433, ZENUSDT=355, TRXUSDT=300, ENAUSDT=290, 币安人生USDT=265

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | watchlist_tier_keep | 1 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 7117 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 666 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 138 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2479 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 659 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 298 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 8 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2471 |
| SR_FLIP_RETEST | filtered | min_confidence | 34 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 10880 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 138 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 54.70 | 50.00 | -4.70 | 23.20 | 20.00 | 17.10 | 0.00 | 15.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 4 | 37.30 | 80.00 | 42.70 | 22.30 | 20.00 | 17.00 | 0.00 | 14.00 |
| FAILED_AUCTION_RECLAIM | filtered | 7783 | 42.28 | 78.72 | 36.44 | 22.77 | 18.12 | 14.00 | 1.23 | 9.64 |
| FAILED_AUCTION_RECLAIM | kept | 138 | 61.14 | 50.00 | -11.14 | 22.81 | 20.00 | 14.00 | 5.00 | 5.95 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3138 | 52.36 | 68.15 | 15.79 | 20.81 | 19.33 | 15.20 | 2.59 | 10.28 |
| QUIET_COMPRESSION_BREAK | filtered | 306 | 46.64 | 65.39 | 18.75 | 20.16 | 18.44 | 15.80 | 0.00 | 17.79 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 82.50 | 80.00 | -2.50 | 23.30 | 19.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 2505 | 32.77 | 65.20 | 32.43 | 21.71 | 19.97 | 15.21 | 1.70 | 15.15 |
| SR_FLIP_RETEST | kept | 10880 | 57.21 | 50.00 | -7.21 | 21.63 | 19.98 | 15.20 | 1.03 | 8.94 |
| TREND_PULLBACK_EMA | filtered | 138 | 72.20 | 80.00 | 7.80 | 18.14 | 19.40 | 20.00 | 5.50 | 9.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 54.70 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 4.70 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 4 | 37.30 | 23.00 | 18.00 | 3.00 | 14.00 | 5.00 | 3.30 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 7783 | 42.28 | 17.41 | 8.79 | 3.02 | 10.94 | 5.24 | 5.47 | 1.23 |
| FAILED_AUCTION_RECLAIM | kept | 138 | 61.14 | 24.99 | 13.39 | 3.00 | 9.04 | 4.98 | 6.68 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3138 | 52.36 | 22.61 | 10.24 | 3.40 | 12.76 | 6.10 | 6.82 | 2.59 |
| QUIET_COMPRESSION_BREAK | filtered | 306 | 46.64 | 17.18 | 18.00 | 3.86 | 13.98 | 8.08 | 4.75 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 82.50 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 2505 | 32.77 | 20.69 | 8.13 | 3.91 | 13.85 | 5.28 | 5.07 | 1.70 |
| SR_FLIP_RETEST | kept | 10880 | 57.21 | 15.12 | 18.00 | 3.51 | 11.17 | 8.49 | 9.68 | 1.03 |
| TREND_PULLBACK_EMA | filtered | 138 | 72.20 | 25.00 | 18.00 | 3.00 | 14.00 | 9.00 | 6.70 | 5.50 |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=2 (50.0%) | PREMATURE=0 (0.0%) | NEUTRAL=2 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 2 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 2 | 0 | 2 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 2 | 0 | 2 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8340990`
- `Path funnel` emissions: `286`
- `Regime distribution` emissions: `286`
- `QUIET_SCALP_BLOCK` events: `5914`
- `confidence_gate` events: `24894`
- `free_channel_post` events: `7`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **7**

| Source | Count |
|---|---:|
| regime_shift | 7 |

- By severity: HIGH=7

## Dependency readiness
- cvd: presence[absent=218530, present=1369573] state[empty=218530, populated=1369573] buckets[many=521395, none=218530, some=848178] sources[none] quality[none]
- funding_rate: presence[absent=4096, present=1584007] state[empty=4096, populated=1584007] buckets[few=1584007, none=4096] sources[none] quality[none]
- liquidation_clusters: presence[absent=1588103] state[empty=1588103] buckets[none=1588103] sources[none] quality[none]
- oi_snapshot: presence[absent=243, present=1587860] state[empty=243, populated=1587860] buckets[few=981, many=1581563, none=243, some=5316] sources[none] quality[none]
- order_book: presence[absent=76726, present=1511377] state[populated=1511377, unavailable=76726] buckets[few=1511377, none=76726] sources[book_ticker=1511377, unavailable=76726] quality[none=76726, top_of_book_only=1511377]
- orderblocks: presence[absent=1588103] state[empty=1588103] buckets[none=1588103] sources[not_implemented=1588103] quality[none]
- recent_ticks: presence[absent=145903, present=1442200] state[empty=145903, populated=1442200] buckets[many=1442200, none=145903] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.007038116455078` sec
- Median create→first breach: `None` sec
- Median create→terminal: `903.4914929866791` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0425 | None | 903.4914929866791 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 62822 | 83 | 25650 | 0.0 | 0.0 | None | None | 37172 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 144 | 0 | 6 | 0.0 | 0.0 | None | None | 138 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `9`
- Gating Δ: `-28619`
- No-generation Δ: `-2057329`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0653, "current_avg_pnl": -0.0425, "current_win_rate": 0.0, "previous_avg_pnl": -0.1078, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 21, "geometry_changed_delta": 0, "geometry_preserved_delta": -556, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 138, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
