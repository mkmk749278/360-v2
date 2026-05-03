# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT, EVAL::POST_DISPLACEMENT_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::WHALE_MOMENTUM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `34026` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1597950 | 1597946 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1597950 | 1597946 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1597950 | 1597942 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1597950 | 1539599 | 58351 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1597950 | 1596252 | 1698 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1597950 | 1597950 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1597950 | 1597950 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1597950 | 1597950 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1597950 | 1597334 | 616 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1597950 | 1525086 | 72864 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1597950 | 1545703 | 52247 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1597950 | 1597949 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1597950 | 1597934 | 16 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1597950 | 1597950 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 58351 | 58351 | 50588 | 6 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1698 | 1698 | 1698 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 52247 | 52247 | 48119 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 616 | 616 | 262 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 72864 | 72864 | 27424 | 108 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 16 | 16 | 16 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1597946): breakout_not_found=628794, regime_blocked=605956, basic_filters_failed=184222, retest_proximity_failed=169914, volume_spike_missing=9054, ema_alignment_reject=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1597946): regime_blocked=1123793, sweeps_not_detected=177400, ema_alignment_reject=162788, basic_filters_failed=118355, adx_reject=13307, momentum_reject=2298, reclaim_confirmation_failed=3, rsi_reject=2
- **EVAL::DIVERGENCE_CONTINUATION** (total=1597942): regime_blocked=1123793, cvd_divergence_failed=256611, basic_filters_failed=118355, missing_cvd=38511, ema_alignment_reject=35481, retest_proximity_failed=25189, missing_fvg_or_orderblock=2
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1539599): regime_blocked=517808, auction_not_detected=515911, basic_filters_failed=318307, reclaim_hold_failed=100551, tail_too_small=86603, rsi_reject=419
- **EVAL::FUNDING_EXTREME** (total=1596252): funding_not_extreme=1177125, basic_filters_failed=377825, missing_funding_rate=21992, ema_alignment_reject=10815, rsi_reject=4858, momentum_reject=3432, cvd_divergence_failed=203, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=1597950): cascade_threshold_not_met=1178460, basic_filters_failed=384169, cvd_divergence_failed=34750, missing_cvd=499, rsi_reject=72
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1597950): feature_disabled=1597950
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1597950): regime_blocked=1123793, breakout_not_found=179707, ema_alignment_reject=162788, basic_filters_failed=118355, adx_reject=13307
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1597334): regime_blocked=991965, breakout_not_detected=223088, basic_filters_failed=199952, compression_not_detected=134081, rsi_reject=30065, macd_reject=10455, missing_fvg_or_orderblock=7728
- **EVAL::SR_FLIP_RETEST** (total=1525086): regime_blocked=517808, retest_out_of_zone=365698, basic_filters_failed=312137, flip_close_not_confirmed=168644, reclaim_hold_failed=133706, insufficient_candles=10157, wick_quality_failed=9009, missing_fvg_or_orderblock=4131, rsi_reject=2811, ema_alignment_reject=985
- **EVAL::STANDARD** (total=1545703): momentum_reject=580309, basic_filters_failed=257748, adx_reject=255408, sweeps_not_detected=241333, ema_alignment_reject=165439, insufficient_candles=20900, macd_reject=15233, invalid_sl_geometry=9219, rsi_reject=110, htf_ema_reject=4
- **EVAL::TREND_PULLBACK** (total=1597949): regime_blocked=1123793, ema_alignment_reject=162768, ema_not_tested_prev=146793, basic_filters_failed=112593, body_conviction_fail=18684, rsi_reject=11504, insufficient_candles=9626, no_ema_reclaim_close=6163, prev_already_below_emas=6016, no_prev_high_break=3, prev_already_above_emas=3, momentum_reject=2, no_prev_low_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1597934): regime_blocked=605956, breakout_not_found=473480, retest_proximity_failed=308150, basic_filters_failed=184222, volume_spike_missing=26094, missing_fvg_or_orderblock=32
- **EVAL::WHALE_MOMENTUM** (total=1597950): momentum_reject=991994, regime_blocked=605956

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 842033 | 39.5% |
| VOLATILE | 669205 | 31.4% |
| TRENDING_UP | 372900 | 17.5% |
| TRENDING_DOWN | 249331 | 11.7% |
| RANGING | 45 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **3912**
- Average confidence gap to threshold: **21.71** (samples=3912) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=1246, WLFIUSDT=405, ZENUSDT=370, ZEREBROUSDT=339, DOTUSDT=338, DASHUSDT=285, ONDOUSDT=272, SOLUSDT=113, ZECUSDT=101, DOGEUSDT=93

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 7183 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 225 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 14 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 2530 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1458 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 303 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 43 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 3557 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2186 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 14624 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 7408 | 41.87 | 79.54 | 37.67 | 22.97 | 18.04 | 14.00 | 1.05 | 8.48 |
| FAILED_AUCTION_RECLAIM | kept | 14 | 56.39 | 50.00 | -6.39 | 21.84 | 20.00 | 14.00 | 5.00 | 5.07 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3988 | 60.69 | 74.52 | 13.83 | 20.89 | 19.20 | 15.20 | 2.79 | 2.60 |
| QUIET_COMPRESSION_BREAK | filtered | 346 | 64.00 | 78.14 | 14.14 | 16.82 | 19.93 | 15.80 | 0.00 | 1.72 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 82.50 | 80.00 | -2.50 | 23.30 | 19.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 5743 | 57.62 | 74.29 | 16.67 | 20.82 | 20.00 | 17.25 | 1.34 | 3.67 |
| SR_FLIP_RETEST | kept | 14624 | 57.57 | 50.00 | -7.57 | 21.57 | 19.98 | 15.20 | 1.02 | 8.56 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 7361 | 41.87 | 17.03 | 8.00 | 3.02 | 11.02 | 5.01 | 5.32 | 1.05 |
| FAILED_AUCTION_RECLAIM | kept | 13 | 56.39 | 24.85 | 8.00 | 3.00 | 9.46 | 4.81 | 6.52 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3084 | 60.69 | 24.10 | 8.00 | 3.41 | 12.47 | 6.98 | 6.79 | 2.79 |
| QUIET_COMPRESSION_BREAK | filtered | 49 | 64.00 | 17.98 | 18.00 | 6.18 | 14.00 | 6.60 | 5.01 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 82.50 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 1939 | 57.62 | 21.31 | 8.06 | 3.45 | 13.72 | 5.08 | 5.06 | 1.34 |
| SR_FLIP_RETEST | kept | 12006 | 57.57 | 15.13 | 18.00 | 3.54 | 11.18 | 8.48 | 9.66 | 1.02 |

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
- Total log lines in window: `8610615`
- `Path funnel` emissions: `289`
- `Regime distribution` emissions: `289`
- `QUIET_SCALP_BLOCK` events: `3912`
- `confidence_gate` events: `32124`
- `free_channel_post` events: `9`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **9**

| Source | Count |
|---|---:|
| regime_shift | 9 |

- By severity: HIGH=9

## Dependency readiness
- cvd: presence[absent=205639, present=1392313] state[empty=205639, populated=1392313] buckets[few=4, many=521123, none=205639, some=871186] sources[none] quality[none]
- funding_rate: presence[absent=21994, present=1575958] state[empty=21994, populated=1575958] buckets[few=1575958, none=21994] sources[none] quality[none]
- liquidation_clusters: presence[absent=1597952] state[empty=1597952] buckets[none=1597952] sources[none] quality[none]
- oi_snapshot: presence[absent=13934, present=1584018] state[empty=13934, populated=1584018] buckets[few=981, many=1577721, none=13934, some=5316] sources[none] quality[none]
- order_book: presence[absent=71191, present=1526761] state[populated=1526761, unavailable=71191] buckets[few=1526761, none=71191] sources[book_ticker=1526761, unavailable=71191] quality[none=71191, top_of_book_only=1526761]
- orderblocks: presence[absent=1597952] state[empty=1597952] buckets[none=1597952] sources[not_implemented=1597952] quality[none]
- recent_ticks: presence[absent=140914, present=1457038] state[empty=140914, populated=1457038] buckets[many=1457038, none=140914] sources[none] quality[none]

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
| SR_FLIP_RETEST | 0 | 72864 | 108 | 27424 | 0.0 | 0.0 | None | None | 45440 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1 | 0 | 1 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `39`
- Gating Δ: `-40647`
- No-generation Δ: `-2213809`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0653, "current_avg_pnl": -0.0425, "current_win_rate": 0.0, "previous_avg_pnl": -0.1078, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 66, "geometry_changed_delta": 0, "geometry_preserved_delta": 15312, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -607.69, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::WHALE_MOMENTUM**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **EVAL::WHALE_MOMENTUM**
