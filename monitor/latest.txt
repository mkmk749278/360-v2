# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `2388` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2170 | 2170 | 2170 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1168 | 1168 | 1164 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1821 | 1821 | 1809 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1718118 | 1715948 | 2170 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1718118 | 1716950 | 1168 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1718118 | 1716297 | 1821 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1718118 | 1686704 | 31414 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1718118 | 1717283 | 835 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1718118 | 1718118 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1718118 | 1718118 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1718118 | 1718118 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1718118 | 1718118 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1718118 | 1715478 | 2640 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1718118 | 1701534 | 16584 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1718118 | 1698023 | 20095 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1718118 | 1718118 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1718118 | 1718091 | 27 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1718118 | 1718118 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 31414 | 31414 | 15011 | 67 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 835 | 835 | 835 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20095 | 20095 | 16684 | 11 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2640 | 2640 | 930 | 13 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 16584 | 16584 | 4359 | 18 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 27 | 27 | 25 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1715948): breakout_not_found=1260547, basic_filters_failed=385673, retest_proximity_failed=65028, volume_spike_missing=3672, ema_alignment_reject=715, missing_fvg_or_orderblock=313
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1716950): regime_blocked=1626276, sweeps_not_detected=32475, ema_alignment_reject=31576, basic_filters_failed=21865, adx_reject=2061, momentum_reject=2055, rsi_reject=626, reclaim_confirmation_failed=16
- **EVAL::DIVERGENCE_CONTINUATION** (total=1716297): regime_blocked=1626276, cvd_divergence_failed=46166, basic_filters_failed=21865, ema_alignment_reject=9144, missing_cvd=5913, retest_proximity_failed=4583, cvd_insufficient=2350
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1686704): regime_blocked=1301697, auction_not_detected=190267, basic_filters_failed=101942, reclaim_hold_failed=64265, tail_too_small=27552, rsi_reject=981
- **EVAL::FUNDING_EXTREME** (total=1717283): funding_not_extreme=1272214, basic_filters_failed=383472, rsi_reject=31171, ema_alignment_reject=20865, missing_funding_rate=6740, momentum_reject=2154, cvd_divergence_failed=667
- **EVAL::LIQUIDATION_REVERSAL** (total=1718118): cascade_threshold_not_met=1324969, basic_filters_failed=385673, cvd_divergence_failed=7358, rsi_reject=118
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1718118): no_ma_cross=1332445, basic_filters_failed=385673
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1718118): feature_disabled=1718118
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1718118): regime_blocked=1626276, breakout_not_found=36340, ema_alignment_reject=31576, basic_filters_failed=21865, adx_reject=2061
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1715478): regime_blocked=1393539, breakout_not_detected=122908, compression_not_detected=99544, basic_filters_failed=80077, rsi_reject=11595, macd_reject=5227, missing_fvg_or_orderblock=2588
- **EVAL::SR_FLIP_RETEST** (total=1701534): regime_blocked=1301697, flip_close_not_confirmed=109737, basic_filters_failed=101942, reclaim_hold_failed=89529, retest_out_of_zone=55898, rsi_reject=20850, wick_quality_failed=12963, missing_fvg_or_orderblock=5373, ema_alignment_reject=3545
- **EVAL::STANDARD** (total=1698023): momentum_reject=821562, basic_filters_failed=364357, adx_reject=187239, ema_alignment_reject=132168, sweeps_not_detected=121178, rsi_reject=62331, macd_reject=7790, invalid_sl_geometry=1395, htf_ema_reject=3
- **EVAL::TREND_PULLBACK** (total=1718118): regime_blocked=1626276, ema_alignment_reject=31576, ema_not_tested_prev=27813, basic_filters_failed=21865, body_conviction_fail=3710, rsi_reject=3395, no_ema_reclaim_close=2433, no_prev_low_break=628, prev_already_above_emas=341, prev_already_below_emas=74, ema21_not_tagged=5, no_prev_high_break=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1718091): breakout_not_found=865177, retest_proximity_failed=412385, basic_filters_failed=385673, volume_spike_missing=29144, rsi_reject=25672, missing_fvg_or_orderblock=40
- **EVAL::WHALE_MOMENTUM** (total=1718118): momentum_reject=1717152, recent_ticks_insufficient=966

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 1582493 | 76.1% |
| QUIET | 363222 | 17.5% |
| TRENDING_DOWN | 61269 | 2.9% |
| TRENDING_UP | 52856 | 2.5% |
| RANGING | 20363 | 1.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **436**
- Average confidence gap to threshold: **13.65** (samples=436) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SKYAIUSDT=289, TRXUSDT=45, WIFUSDT=28, LABUSDT=20, NATGASUSDT=12, ETHUSDT=9, BTCUSDT=9, DOGEUSDT=6, TONUSDT=6, ZECUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 12 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 1213 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 63 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 11957 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 321 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1288 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 42 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1520 |
| SR_FLIP_RETEST | filtered | min_confidence | 1338 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 10 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 39 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 3 | 60.57 | 65.00 | 4.43 | 23.40 | 18.40 | 17.00 | 0.00 | -3.00 |
| DIVERGENCE_CONTINUATION | kept | 12 | 68.80 | 65.00 | -3.80 | 19.23 | 20.00 | 20.00 | 6.50 | -3.00 |
| FAILED_AUCTION_RECLAIM | filtered | 1276 | 60.69 | 65.00 | 4.31 | 23.07 | 18.03 | 14.00 | 3.49 | 6.10 |
| FAILED_AUCTION_RECLAIM | kept | 11957 | 72.13 | 65.00 | -7.13 | 21.22 | 20.00 | 14.00 | 5.03 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 324 | 49.81 | 65.00 | 15.19 | 20.82 | 19.89 | 15.20 | 2.93 | 19.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1288 | 67.36 | 65.00 | -2.36 | 21.72 | 19.30 | 15.20 | 4.14 | -0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 42 | 55.00 | 65.00 | 10.00 | 21.60 | 19.51 | 15.80 | 0.00 | 9.35 |
| QUIET_COMPRESSION_BREAK | kept | 1520 | 74.50 | 65.00 | -9.50 | 20.98 | 18.22 | 15.80 | 0.00 | -1.56 |
| SR_FLIP_RETEST | filtered | 1348 | 59.02 | 65.00 | 5.98 | 21.67 | 19.97 | 15.33 | 1.05 | 7.48 |
| SR_FLIP_RETEST | kept | 39 | 69.69 | 65.00 | -4.69 | 21.69 | 19.99 | 16.48 | 1.62 | 2.03 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 64.00 | 65.00 | 1.00 | 22.45 | 18.80 | 20.00 | 3.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 3 | 60.57 | 25.00 | 18.00 | 4.00 | 15.00 | 7.67 | 5.90 | 0.00 |
| DIVERGENCE_CONTINUATION | kept | 12 | 68.80 | 17.00 | 18.00 | 3.00 | 10.00 | 5.00 | 9.30 | 6.50 |
| FAILED_AUCTION_RECLAIM | filtered | 1276 | 60.69 | 24.91 | 14.00 | 3.06 | 11.04 | 5.01 | 5.33 | 3.49 |
| FAILED_AUCTION_RECLAIM | kept | 11957 | 72.13 | 24.99 | 14.31 | 3.03 | 11.49 | 4.98 | 8.30 | 5.03 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 324 | 49.81 | 24.49 | 14.04 | 6.30 | 12.12 | 2.81 | 8.30 | 2.93 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1288 | 67.36 | 18.23 | 14.01 | 4.06 | 12.27 | 7.49 | 7.16 | 4.14 |
| QUIET_COMPRESSION_BREAK | filtered | 42 | 55.00 | 17.19 | 18.00 | 12.29 | 14.00 | 7.52 | 5.70 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1520 | 74.50 | 23.38 | 18.00 | 4.48 | 14.15 | 8.11 | 6.38 | 0.00 |
| SR_FLIP_RETEST | filtered | 1348 | 59.02 | 15.97 | 17.93 | 3.97 | 11.59 | 8.22 | 9.37 | 1.05 |
| SR_FLIP_RETEST | kept | 39 | 69.69 | 19.82 | 16.46 | 7.23 | 13.82 | 5.38 | 9.20 | 1.62 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 64.00 | 25.00 | 20.00 | 3.00 | 14.00 | 5.00 | 9.00 | 3.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 3 | 60.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 12 | 68.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 1276 | 60.69 | 0.00 | 0.00 | 0.01 | 0.00 | 0.12 | 0.00 | **0.13** |
| FAILED_AUCTION_RECLAIM | kept | 11957 | 72.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 324 | 49.81 | 0.00 | 0.00 | 0.04 | 0.00 | 19.67 | 0.00 | **19.71** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1288 | 67.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 42 | 55.00 | 5.14 | 0.00 | 0.69 | 0.00 | 3.38 | 0.00 | **9.21** |
| QUIET_COMPRESSION_BREAK | kept | 1520 | 74.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | **0.01** |
| SR_FLIP_RETEST | filtered | 1348 | 59.02 | 0.00 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **0.28** |
| SR_FLIP_RETEST | kept | 39 | 69.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 64.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=11 (25.6%) | PREMATURE=2 (4.7%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 9 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 5 | 1 | 28 | 0 |
| other | 5 | 0 | 1 | 0 |
| regime_shift | 1 | 1 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 5 | 0 | 27 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 4 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `9129822`
- `Path funnel` emissions: `278`
- `Regime distribution` emissions: `278`
- `QUIET_SCALP_BLOCK` events: `436`
- `confidence_gate` events: `17811`
- `free_channel_post` events: `24`
- `pre_tp_fire` events: `11`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **11**
- Avg resolved threshold: **0.313%** raw → avg net **+2.43%** @ 10x
- Avg time-to-fire from dispatch: **530s**
- By threshold source: stamped=11

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| QUIET_COMPRESSION_BREAK | 4 | 0.200% | +1.30% | 536 | stamped=4 |
| SR_FLIP_RETEST | 3 | 0.379% | +3.09% | 712 | stamped=3 |
| FAILED_AUCTION_RECLAIM | 3 | 0.328% | +2.58% | 446 | stamped=3 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 0.521% | +4.51% | 214 | stamped=1 |
- Top symbols: SOLUSDT=3, TONUSDT=2, DOGEUSDT=2, BZUSDT=2, XRPUSDT=1, LABUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **58**

| Label | REST-fallback activations |
|---|---:|
| futures | 58 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **24**

| Source | Count |
|---|---:|
| pre_tp | 11 |
| signal_close | 7 |
| regime_shift | 5 |
| signal_highlight | 1 |

- By severity: HIGH=24

## Dependency readiness
- cvd: presence[absent=67435, present=1650684] state[empty=67435, populated=1650684] buckets[many=1586838, none=67435, some=63846] sources[none] quality[none]
- funding_rate: presence[absent=6741, present=1711378] state[empty=6741, populated=1711378] buckets[few=1711378, none=6741] sources[none] quality[none]
- liquidation_clusters: presence[absent=1718119] state[empty=1718119] buckets[none=1718119] sources[none] quality[none]
- oi_snapshot: presence[absent=835, present=1717284] state[empty=835, populated=1717284] buckets[few=1589, many=1707452, none=835, some=8243] sources[none] quality[none]
- order_book: presence[absent=69026, present=1649093] state[populated=1649093, unavailable=69026] buckets[few=1649093, none=69026] sources[book_ticker=1649093, unavailable=69026] quality[none=69026, top_of_book_only=1649093]
- orderblocks: presence[absent=1718119] state[empty=1718119] buckets[none=1718119] sources[not_implemented=1718119] quality[none]
- recent_ticks: presence[absent=62446, present=1655673] state[empty=62446, populated=1655673] buckets[many=1655673, none=62446] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.8166918754577637` sec
- Median create→first breach: `1774.2603499889374` sec
- Median create→terminal: `905.4202079772949` sec
- Median first breach→terminal: `0.48166704177856445` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 3.2}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 13 | 13 | 0.0 | 7.7 | 0.0 | -0.0708 | 1835.00599193573 | 1027.3235654830933 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 7 | 0.0 | 0.0 | 0.0 | 0.0893 | None | 605.5420950651169 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 0.0 | 0.0 | 0.0 | 0.2139 | 558.8982933759689 | 905.4202079772949 |
| SR_FLIP_RETEST | 8 | 8 | 0.0 | 0.0 | 0.0 | 0.0769 | None | 1915.578947544098 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 16584 | 18 | 4359 | 0.0 | 0.0 | None | 1915.578947544098 | 12225 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `13`
- Gating Δ: `-97611`
- No-generation Δ: `3573433`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0708, "current_avg_pnl": -0.0708, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0893, "current_avg_pnl": 0.0893, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.2139, "current_avg_pnl": 0.2139, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0769, "current_avg_pnl": 0.0769, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -19, "geometry_changed_delta": 0, "geometry_preserved_delta": -65730, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 1915.58, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -8, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **BREAKDOWN_SHORT**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
