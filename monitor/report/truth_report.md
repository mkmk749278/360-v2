# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `12559` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1036 | 1036 | 1032 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17388 | 17388 | 17379 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1601208 | 1601206 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1426617 | 1425581 | 1036 | 0 | 0 | 0 | low-sample (sweeps_not_detected) |
| EVAL::DIVERGENCE_CONTINUATION | 1426617 | 1409229 | 17388 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1426617 | 1377384 | 49233 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1601208 | 1598642 | 2566 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1601208 | 1601208 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1426617 | 1426615 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1601208 | 1601208 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1426617 | 1426617 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1426617 | 1426590 | 27 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1426617 | 1291368 | 135249 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1426617 | 1382245 | 44372 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1426617 | 1426613 | 4 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1601208 | 1601194 | 14 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1601208 | 1601208 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 49233 | 49233 | 24715 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2566 | 2566 | 2566 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 44372 | 44372 | 2425 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 1 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 27 | 27 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 135249 | 135249 | 2272 | 35 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4 | 4 | 3 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 14 | 14 | 13 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1601206): breakout_not_found=964129, basic_filters_failed=485886, retest_proximity_failed=122469, volume_spike_missing=27060, ema_alignment_reject=1662
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1425581): sweeps_not_detected=352830, regime_blocked=347637, basic_filters_failed=325586, ema_alignment_reject=221651, rsi_reject=83712, adx_reject=64298, momentum_reject=29648, reclaim_confirmation_failed=219
- **EVAL::DIVERGENCE_CONTINUATION** (total=1409229): cvd_divergence_failed=585389, regime_blocked=347637, basic_filters_failed=325586, missing_cvd=74103, cvd_insufficient=35494, ema_alignment_reject=22418, retest_proximity_failed=18587, missing_fvg_or_orderblock=15
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1377384): auction_not_detected=562455, basic_filters_failed=422117, reclaim_hold_failed=229164, tail_too_small=163648
- **EVAL::FUNDING_EXTREME** (total=1598642): funding_not_extreme=1069957, basic_filters_failed=473783, missing_funding_rate=28066, rsi_reject=24524, ema_alignment_reject=1268, momentum_reject=732, missing_fvg_or_orderblock=312
- **EVAL::LIQUIDATION_REVERSAL** (total=1601208): cascade_threshold_not_met=1097789, basic_filters_failed=485886, cvd_divergence_failed=17533
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1426615): no_ma_cross=997740, basic_filters_failed=422117, ma_cross_cooldown=6758
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1601208): feature_disabled=1601208
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1426617): breakout_not_found=467445, regime_blocked=347637, basic_filters_failed=325586, ema_alignment_reject=221651, adx_reject=64298
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1426590): regime_blocked=1078980, compression_not_detected=113730, basic_filters_failed=96531, breakout_not_detected=95528, missing_fvg_or_orderblock=23891, macd_reject=17930
- **EVAL::SR_FLIP_RETEST** (total=1291368): basic_filters_failed=422117, flip_close_not_confirmed=279267, retest_out_of_zone=231855, reclaim_hold_failed=217422, wick_quality_failed=90535, rsi_reject=49552, ema_alignment_reject=620
- **EVAL::STANDARD** (total=1382245): momentum_reject=562945, basic_filters_failed=315020, adx_reject=256877, ema_alignment_reject=95667, sweeps_not_detected=90638, macd_reject=44992, rsi_reject=16105, invalid_sl_geometry=1
- **EVAL::TREND_PULLBACK** (total=1426613): ema_not_tested_prev=379857, regime_blocked=347637, basic_filters_failed=325586, ema_alignment_reject=262848, no_ema_reclaim_close=62176, body_conviction_fail=28102, rsi_reject=13932, no_prev_high_break=6460, prev_already_above_emas=14, prev_already_below_emas=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1601194): breakout_not_found=610742, basic_filters_failed=485886, retest_proximity_failed=461093, ema_alignment_reject=24988, volume_spike_missing=18200, missing_fvg_or_orderblock=285
- **EVAL::WHALE_MOMENTUM** (total=1601208): momentum_reject=1059752, recent_ticks_insufficient=419546, basic_filters_failed=121910

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1256883 | 70.0% |
| QUIET | 488529 | 27.2% |
| TRENDING_DOWN | 47185 | 2.6% |
| RANGING | 3072 | 0.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **295**
- Average confidence gap to threshold: **15.07** (samples=295) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SKYAIUSDT=278, SUIUSDT=17

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 6 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 278 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 963 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | filtered | min_confidence | 21817 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 14758 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 3 | 71.33 | 65.00 | -6.33 | 19.47 | 20.00 | 19.00 | 2.00 | -1.00 |
| DIVERGENCE_CONTINUATION | kept | 6 | 68.33 | 65.00 | -3.33 | 20.78 | 19.97 | 17.55 | 4.50 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 55.20 | 65.00 | 9.80 | 21.30 | 20.00 | 14.00 | 5.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.00 | 65.00 | -2.00 | 20.90 | 20.00 | 14.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 278 | 49.61 | 65.00 | 15.39 | 20.62 | 20.00 | 15.20 | 3.01 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 963 | 67.80 | 65.00 | -2.80 | 20.27 | 20.00 | 15.20 | 3.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 75.00 | 65.00 | -10.00 | 22.50 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 21817 | 52.69 | 65.00 | 12.31 | 19.53 | 19.97 | 15.27 | 2.68 | 6.82 |
| SR_FLIP_RETEST | kept | 14758 | 71.32 | 65.00 | -6.32 | 20.76 | 20.00 | 15.20 | 2.17 | 2.87 |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 65.00 | -4.20 | 22.00 | 19.80 | 20.00 | 5.50 | -3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 3 | 71.33 | 22.33 | 18.00 | 3.00 | 13.00 | 5.83 | 7.17 | 2.00 |
| DIVERGENCE_CONTINUATION | kept | 6 | 68.33 | 18.33 | 18.00 | 3.00 | 13.50 | 4.58 | 6.42 | 4.50 |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 55.20 | 25.00 | 14.00 | 3.00 | 12.00 | 8.50 | 2.70 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.00 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 3.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 278 | 49.61 | 25.00 | 14.00 | 6.00 | 12.00 | 2.50 | 8.70 | 3.01 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 963 | 67.80 | 25.00 | 14.00 | 3.00 | 12.00 | 5.50 | 5.30 | 3.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 75.00 | 17.00 | 18.00 | 6.00 | 14.00 | 10.00 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 21817 | 52.69 | 23.12 | 18.00 | 3.00 | 15.89 | 5.00 | 3.78 | 2.68 |
| SR_FLIP_RETEST | kept | 14758 | 71.32 | 20.55 | 18.00 | 4.67 | 12.66 | 7.76 | 10.00 | 2.17 |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 6.70 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 3 | 71.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 6 | 68.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 55.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 278 | 49.61 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 963 | 67.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 75.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 21817 | 52.69 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | **0.80** |
| SR_FLIP_RETEST | kept | 14758 | 71.32 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **0.09** |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=7 (100.0%) | PREMATURE=0 (0.0%) | NEUTRAL=0 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 7 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| other | 3 | 0 | 0 | 0 |
| regime_shift | 4 | 0 | 0 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 0 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 1 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 1 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `9575589`
- `Path funnel` emissions: `241`
- `Regime distribution` emissions: `241`
- `QUIET_SCALP_BLOCK` events: `295`
- `confidence_gate` events: `37850`
- `free_channel_post` events: `3`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **162**
- Total REST-fallback activations: **76**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 152 | 2723 | 4370 | 5447 | 0 |
| futures_liq | 10 | 1969 | 3115 | 3234 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 76 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[absent=150413, present=1450795] state[empty=150413, populated=1450795] buckets[many=1289711, none=150413, some=161084] sources[none] quality[none]
- funding_rate: presence[absent=28066, present=1573142] state[empty=28066, populated=1573142] buckets[few=1573142, none=28066] sources[none] quality[none]
- liquidation_clusters: presence[absent=1601208] state[empty=1601208] buckets[none=1601208] sources[none] quality[none]
- oi_snapshot: presence[absent=19675, present=1581533] state[empty=19675, populated=1581533] buckets[few=246, many=1579919, none=19675, some=1368] sources[none] quality[none]
- order_book: presence[absent=61066, present=1540142] state[populated=1540142, unavailable=61066] buckets[few=1540142, none=61066] sources[book_ticker=1540142, unavailable=61066] quality[none=61066, top_of_book_only=1540142]
- orderblocks: presence[absent=1601208] state[empty=1601208] buckets[none=1601208] sources[not_implemented=1601208] quality[none]
- recent_ticks: presence[absent=89787, present=1511421] state[empty=89787, populated=1511421] buckets[many=1511421, none=89787] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.6756709814071655` sec
- Median create→first breach: `892.5536189079285` sec
- Median create→terminal: `1874.42209649086` sec
- Median first breach→terminal: `0.7338249683380127` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.12 | None | 2832.8378698825836 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.2506 | None | 608.4884419441223 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0161 | None | 962.6704878807068 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 50.0 | 0.0 | -0.3896 | 892.5536189079285 | 1383.347585439682 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.1115 | None | None |
| SR_FLIP_RETEST | 21 | 21 | 0.0 | 0.0 | 0.0 | -0.077 | None | 3601.6969270706177 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 1.1262 | None | None |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 135249 | 35 | 2272 | 0.0 | 0.0 | None | 3601.6969270706177 | 132977 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4 | 1 | 3 | 0.0 | 0.0 | None | None | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `38`
- Gating Δ: `-16804`
- No-generation Δ: `-4912208`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.1885, "current_avg_pnl": -0.077, "current_win_rate": 0.0, "previous_avg_pnl": 0.1115, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 30, "geometry_changed_delta": 0, "geometry_preserved_delta": -36398, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 3601.7, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
