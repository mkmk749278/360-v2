# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `4375` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 27102 | 27102 | 27102 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1050 | 1050 | 1050 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1878285 | 1878285 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1878285 | 1851183 | 27102 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::DIVERGENCE_CONTINUATION | 1878285 | 1877235 | 1050 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1878285 | 1822964 | 55321 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1878285 | 1878285 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1878285 | 1878285 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1878285 | 1878285 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1878285 | 1878285 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1878285 | 1878285 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1878285 | 1861813 | 16472 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1878285 | 1772403 | 105882 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1878285 | 1836108 | 42177 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1878285 | 1878283 | 2 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1878285 | 1878285 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1878285 | 1878285 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 55321 | 55321 | 31373 | 54 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 42177 | 42177 | 29458 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 16472 | 16472 | 0 | 48 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 105882 | 105882 | 6335 | 17 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1878285): breakout_not_found=1159567, basic_filters_failed=577401, retest_proximity_failed=130018, ema_alignment_reject=11299
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1851183): basic_filters_failed=445617, ema_alignment_reject=400879, regime_blocked=368527, sweeps_not_detected=343679, rsi_reject=170501, adx_reject=68598, momentum_reject=53379, reclaim_confirmation_failed=3
- **EVAL::DIVERGENCE_CONTINUATION** (total=1877235): cvd_divergence_failed=818195, basic_filters_failed=445617, regime_blocked=368527, retest_proximity_failed=112512, missing_cvd=58792, cvd_insufficient=53621, ema_alignment_reject=19971
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1822964): auction_not_detected=752890, basic_filters_failed=577401, reclaim_hold_failed=338770, tail_too_small=153903
- **EVAL::FUNDING_EXTREME** (total=1878285): funding_not_extreme=1285672, basic_filters_failed=576016, rsi_reject=9399, missing_funding_rate=4587, momentum_reject=1541, ema_alignment_reject=1070
- **EVAL::LIQUIDATION_REVERSAL** (total=1878285): cascade_threshold_not_met=1263183, basic_filters_failed=577401, cvd_divergence_failed=35394, missing_cvd=2112, rsi_reject=195
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1878285): no_ma_cross=1300884, basic_filters_failed=577401
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1878285): feature_disabled=1878285
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1878285): breakout_not_found=594664, basic_filters_failed=445617, ema_alignment_reject=400879, regime_blocked=368527, adx_reject=68598
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1861813): regime_blocked=1509758, basic_filters_failed=131784, compression_not_detected=106784, breakout_not_detected=85962, macd_reject=25943, rsi_reject=1582
- **EVAL::SR_FLIP_RETEST** (total=1772403): basic_filters_failed=577401, flip_close_not_confirmed=411838, retest_out_of_zone=336416, reclaim_hold_failed=264200, wick_quality_failed=120139, rsi_reject=62078, missing_fvg_or_orderblock=331
- **EVAL::STANDARD** (total=1836108): momentum_reject=830999, basic_filters_failed=405144, adx_reject=206036, sweeps_not_detected=146873, ema_alignment_reject=132703, rsi_reject=65777, macd_reject=48576
- **EVAL::TREND_PULLBACK** (total=1878283): ema_not_tested_prev=522840, basic_filters_failed=445617, ema_alignment_reject=400879, regime_blocked=368527, body_conviction_fail=53980, rsi_reject=38310, no_ema_reclaim_close=27797, no_prev_high_break=20331, prev_already_above_emas=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1878285): breakout_not_found=918202, basic_filters_failed=577401, retest_proximity_failed=332325, rsi_reject=30143, volume_spike_missing=20214
- **EVAL::WHALE_MOMENTUM** (total=1878285): momentum_reject=1876776, recent_ticks_insufficient=1509

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1545297 | 69.2% |
| QUIET | 436194 | 19.5% |
| TRENDING_DOWN | 252437 | 11.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1341**
- Average confidence gap to threshold: **0.35** (samples=1341) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ZECUSDT=1322, DOGEUSDT=19

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 2024 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1322 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 19510 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 16595 |
| SR_FLIP_RETEST | filtered | min_confidence | 20818 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 19 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 755 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3346 | 55.91 | 65.00 | 9.09 | 21.49 | 17.84 | 14.00 | 5.60 | 3.75 |
| FAILED_AUCTION_RECLAIM | kept | 19510 | 70.75 | 65.00 | -5.75 | 21.26 | 20.00 | 14.00 | 5.05 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 16595 | 66.70 | 65.00 | -1.70 | 19.89 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 20837 | 50.43 | 65.00 | 14.57 | 19.78 | 20.00 | 15.20 | 2.52 | 5.22 |
| SR_FLIP_RETEST | kept | 755 | 66.33 | 65.00 | -1.33 | 20.80 | 20.00 | 15.20 | 2.29 | 1.07 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3346 | 55.91 | 24.21 | 14.00 | 3.00 | 9.00 | 6.39 | 6.51 | 5.60 |
| FAILED_AUCTION_RECLAIM | kept | 19510 | 70.75 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 6.70 | 5.05 |
| QUIET_COMPRESSION_BREAK | kept | 16595 | 66.70 | 17.00 | 18.00 | 3.00 | 14.00 | 10.00 | 4.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 20837 | 50.43 | 23.15 | 17.99 | 3.00 | 16.54 | 5.00 | 2.44 | 2.52 |
| SR_FLIP_RETEST | kept | 755 | 66.33 | 21.65 | 12.23 | 3.00 | 15.74 | 7.03 | 6.71 | 2.29 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3346 | 55.91 | 0.00 | 0.00 | 1.77 | 0.00 | 0.00 | 0.00 | **1.77** |
| FAILED_AUCTION_RECLAIM | kept | 19510 | 70.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 16595 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 20837 | 50.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 755 | 66.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=20 (38.5%) | PREMATURE=2 (3.8%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 18 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 6 | 1 | 28 | 0 |
| other | 5 | 0 | 1 | 0 |
| regime_shift | 9 | 1 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 6 | 0 | 27 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 12 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `11046068`
- `Path funnel` emissions: `299`
- `Regime distribution` emissions: `299`
- `QUIET_SCALP_BLOCK` events: `1341`
- `confidence_gate` events: `61043`
- `free_channel_post` events: `7`
- `pre_tp_fire` events: `2`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **2**
- Avg resolved threshold: **0.233%** raw → avg net **+1.62%** @ 10x
- Avg time-to-fire from dispatch: **964s**
- By threshold source: stamped=2

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 1 | 0.265% | +1.95% | 963 | stamped=1 |
| FAILED_AUCTION_RECLAIM | 1 | 0.200% | +1.30% | 964 | stamped=1 |
- Top symbols: TONUSDT=1, DOGEUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **185**
- Total REST-fallback activations: **88**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 175 | 2774 | 4190 | 12269 | 0 |
| futures_liq | 10 | 1883 | 2425 | 2562 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 88 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **7**

| Source | Count |
|---|---:|
| regime_shift | 4 |
| pre_tp | 2 |
| signal_close | 1 |

- By severity: HIGH=7

## Dependency readiness
- cvd: presence[absent=125174, present=1753111] state[empty=125174, populated=1753111] buckets[many=1598539, none=125174, some=154572] sources[none] quality[none]
- funding_rate: presence[absent=4587, present=1873698] state[empty=4587, populated=1873698] buckets[few=1873698, none=4587] sources[none] quality[none]
- liquidation_clusters: presence[absent=1878285] state[empty=1878285] buckets[none=1878285] sources[none] quality[none]
- oi_snapshot: presence[absent=602, present=1877683] state[empty=602, populated=1877683] buckets[few=946, many=1872761, none=602, some=3976] sources[none] quality[none]
- order_book: presence[absent=85754, present=1792531] state[populated=1792531, unavailable=85754] buckets[few=1792531, none=85754] sources[book_ticker=1792531, unavailable=85754] quality[none=85754, top_of_book_only=1792531]
- orderblocks: presence[absent=1878285] state[empty=1878285] buckets[none=1878285] sources[not_implemented=1878285] quality[none]
- recent_ticks: presence[absent=126878, present=1751407] state[empty=126878, populated=1751407] buckets[many=1751407, none=126878] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.2424428462982178` sec
- Median create→first breach: `2886.148158788681` sec
- Median create→terminal: `663.1577041149139` sec
- Median first breach→terminal: `1.9931271076202393` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0866 | None | None |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1774 | None | None |
| SR_FLIP_RETEST | 14 | 14 | 0.0 | 0.0 | 0.0 | -0.0133 | 2886.148158788681 | 663.1577041149139 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 105882 | 17 | 6335 | 0.0 | 0.0 | 2886.148158788681 | 663.1577041149139 | 99547 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2 | 0 | 2 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `18`
- Gating Δ: `77167`
- No-generation Δ: `-1466841`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0959, "current_avg_pnl": 0.0866, "current_win_rate": 0.0, "previous_avg_pnl": -0.0093, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0317, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.0317, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.628, "current_avg_pnl": -0.1774, "current_win_rate": 0.0, "previous_avg_pnl": 0.4506, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.228, "current_avg_pnl": -0.0133, "current_win_rate": 0.0, "previous_avg_pnl": 0.2147, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": 76969, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2886.15, "median_terminal_delta_sec": -2241.55, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
