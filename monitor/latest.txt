# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, LIQUIDITY_SWEEP_REVERSAL, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `735` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 913 | 913 | 913 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 475 | 475 | 474 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 20718 | 20718 | 20715 | 1 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1882120 | 1881207 | 913 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1684776 | 1684301 | 475 | 0 | 0 | 0 | low-sample (sweeps_not_detected) |
| EVAL::DIVERGENCE_CONTINUATION | 1684776 | 1664058 | 20718 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1684776 | 1629069 | 55707 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1882120 | 1874998 | 7122 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1882120 | 1882120 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1684776 | 1684773 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1882120 | 1882120 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1684776 | 1684776 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1684776 | 1680610 | 4166 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1684776 | 1521696 | 163080 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1684776 | 1643607 | 41169 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1684776 | 1684774 | 2 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1882120 | 1882120 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1882120 | 1882120 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 55707 | 55707 | 26170 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 7122 | 7122 | 5898 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 41169 | 41169 | 1430 | 6 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 2 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4166 | 4166 | 3459 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 163080 | 163080 | 2159 | 28 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2 | 2 | 1 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1881207): breakout_not_found=1134367, basic_filters_failed=553686, retest_proximity_failed=157682, volume_spike_missing=34108, ema_alignment_reject=1364
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1684301): sweeps_not_detected=434894, basic_filters_failed=416923, regime_blocked=333390, ema_alignment_reject=268686, adx_reject=94817, rsi_reject=94330, momentum_reject=41256, reclaim_confirmation_failed=5
- **EVAL::DIVERGENCE_CONTINUATION** (total=1664058): cvd_divergence_failed=739429, basic_filters_failed=416923, regime_blocked=333390, missing_cvd=83135, cvd_insufficient=31491, retest_proximity_failed=29918, ema_alignment_reject=29771, missing_fvg_or_orderblock=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1629069): auction_not_detected=652849, basic_filters_failed=494272, reclaim_hold_failed=280611, tail_too_small=201337
- **EVAL::FUNDING_EXTREME** (total=1874998): funding_not_extreme=1280112, basic_filters_failed=545934, rsi_reject=26064, missing_funding_rate=21428, ema_alignment_reject=1148, missing_fvg_or_orderblock=312
- **EVAL::LIQUIDATION_REVERSAL** (total=1882120): cascade_threshold_not_met=1306888, basic_filters_failed=553686, cvd_divergence_failed=21546
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1684773): no_ma_cross=1183961, basic_filters_failed=494272, ma_cross_cooldown=6540
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1882120): feature_disabled=1882120
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1684776): breakout_not_found=570960, basic_filters_failed=416923, regime_blocked=333390, ema_alignment_reject=268686, adx_reject=94817
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1680610): regime_blocked=1351386, compression_not_detected=101585, breakout_not_detected=101557, basic_filters_failed=77349, missing_fvg_or_orderblock=27691, macd_reject=21042
- **EVAL::SR_FLIP_RETEST** (total=1521696): basic_filters_failed=494272, flip_close_not_confirmed=329465, retest_out_of_zone=279731, reclaim_hold_failed=239886, wick_quality_failed=118785, rsi_reject=57881, ema_alignment_reject=1676
- **EVAL::STANDARD** (total=1643607): momentum_reject=642405, basic_filters_failed=354454, adx_reject=350259, ema_alignment_reject=114114, sweeps_not_detected=112931, macd_reject=52297, rsi_reject=16846, invalid_sl_geometry=301
- **EVAL::TREND_PULLBACK** (total=1684774): ema_not_tested_prev=462153, basic_filters_failed=416923, ema_alignment_reject=342458, regime_blocked=333390, no_ema_reclaim_close=66227, body_conviction_fail=42301, no_prev_high_break=12854, rsi_reject=8468
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1882120): breakout_not_found=740140, basic_filters_failed=553686, retest_proximity_failed=534030, ema_alignment_reject=32017, volume_spike_missing=21962, missing_fvg_or_orderblock=285
- **EVAL::WHALE_MOMENTUM** (total=1882120): momentum_reject=1237082, recent_ticks_insufficient=494262, basic_filters_failed=150776

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1557027 | 74.4% |
| QUIET | 442502 | 21.2% |
| TRENDING_DOWN | 73611 | 3.5% |
| RANGING | 18729 | 0.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **255**
- Average confidence gap to threshold: **11.00** (samples=255) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SKYAIUSDT=140, SUIUSDT=111, LDOUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 140 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 4154 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 98 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 312 |
| SR_FLIP_RETEST | filtered | min_confidence | 32362 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 15951 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 74.30 | 65.00 | -9.30 | 20.80 | 20.00 | 17.00 | 2.00 | 0.00 |
| DIVERGENCE_CONTINUATION | kept | 1 | 68.00 | 65.00 | -3.00 | 21.40 | 19.80 | 16.80 | 7.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 55.20 | 65.00 | 9.80 | 21.30 | 20.00 | 14.00 | 5.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.00 | 65.00 | -2.00 | 20.90 | 20.00 | 14.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 140 | 49.60 | 65.00 | 15.40 | 20.75 | 20.00 | 15.20 | 3.00 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 4154 | 67.80 | 65.00 | -2.80 | 20.28 | 20.00 | 15.20 | 3.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 98 | 60.08 | 65.00 | 4.92 | 21.99 | 16.90 | 15.80 | 0.00 | 5.93 |
| QUIET_COMPRESSION_BREAK | kept | 312 | 71.43 | 65.00 | -6.43 | 21.72 | 19.81 | 15.80 | 0.00 | 5.79 |
| SR_FLIP_RETEST | filtered | 32362 | 52.44 | 65.00 | 12.56 | 19.63 | 19.98 | 15.25 | 2.65 | 6.59 |
| SR_FLIP_RETEST | kept | 15951 | 70.38 | 65.00 | -5.38 | 20.38 | 20.00 | 15.20 | 2.40 | 4.24 |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 65.00 | -4.20 | 22.00 | 19.80 | 20.00 | 5.50 | -3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 74.30 | 25.00 | 18.00 | 3.00 | 11.00 | 10.00 | 5.30 | 2.00 |
| DIVERGENCE_CONTINUATION | kept | 1 | 68.00 | 17.00 | 18.00 | 3.00 | 13.00 | 5.00 | 5.00 | 7.00 |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 55.20 | 25.00 | 14.00 | 3.00 | 12.00 | 8.50 | 2.70 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.00 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 3.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 140 | 49.60 | 25.00 | 14.00 | 6.00 | 12.00 | 2.50 | 8.70 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 4154 | 67.80 | 25.00 | 14.00 | 3.00 | 12.00 | 5.50 | 5.30 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 98 | 60.08 | 17.00 | 18.00 | 9.24 | 14.00 | 5.00 | 3.38 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 312 | 71.43 | 24.72 | 18.00 | 8.89 | 16.89 | 5.18 | 3.54 | 0.00 |
| SR_FLIP_RETEST | filtered | 32362 | 52.44 | 23.12 | 18.00 | 3.00 | 16.03 | 5.00 | 3.58 | 2.65 |
| SR_FLIP_RETEST | kept | 15951 | 70.38 | 21.23 | 17.99 | 4.41 | 12.41 | 7.35 | 10.00 | 2.40 |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 6.70 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 74.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 1 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 55.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 140 | 49.60 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 4154 | 67.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 98 | 60.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.00 | **0.18** |
| QUIET_COMPRESSION_BREAK | kept | 312 | 71.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 32362 | 52.44 | 0.00 | 0.00 | 0.71 | 0.00 | 0.00 | 0.00 | **0.71** |
| SR_FLIP_RETEST | kept | 15951 | 70.38 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **0.36** |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=6 (100.0%) | PREMATURE=0 (0.0%) | NEUTRAL=0 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 6 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| other | 2 | 0 | 0 | 0 |
| regime_shift | 4 | 0 | 0 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 1 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `10856660`
- `Path funnel` emissions: `280`
- `Regime distribution` emissions: `280`
- `QUIET_SCALP_BLOCK` events: `255`
- `confidence_gate` events: `53038`
- `free_channel_post` events: `3`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **184**
- Total REST-fallback activations: **87**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 174 | 2615 | 4258 | 5447 | 0 |
| futures_liq | 10 | 2182 | 3234 | 3420 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 87 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[absent=177490, present=1704630] state[empty=177490, populated=1704630] buckets[many=1521978, none=177490, some=182652] sources[none] quality[none]
- funding_rate: presence[absent=21428, present=1860692] state[empty=21428, populated=1860692] buckets[few=1860692, none=21428] sources[none] quality[none]
- liquidation_clusters: presence[absent=1882120] state[empty=1882120] buckets[none=1882120] sources[none] quality[none]
- oi_snapshot: presence[absent=9414, present=1872706] state[empty=9414, populated=1872706] buckets[few=563, many=1869816, none=9414, some=2327] sources[none] quality[none]
- order_book: presence[absent=72530, present=1809590] state[populated=1809590, unavailable=72530] buckets[few=1809590, none=72530] sources[book_ticker=1809590, unavailable=72530] quality[none=72530, top_of_book_only=1809590]
- orderblocks: presence[absent=1882120] state[empty=1882120] buckets[none=1882120] sources[not_implemented=1882120] quality[none]
- recent_ticks: presence[absent=111301, present=1770819] state[empty=111301, populated=1770819] buckets[many=1770819, none=111301] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.7425329685211182` sec
- Median create→first breach: `892.5536189079285` sec
- Median create→terminal: `2190.973512172699` sec
- Median first breach→terminal: `0.7338249683380127` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.12 | None | 2832.8378698825836 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0161 | None | 962.6704878807068 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 0.0 | 25.0 | 0.0 | -0.1844 | 892.5536189079285 | 2032.1906195878983 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.1115 | None | None |
| SR_FLIP_RETEST | 16 | 16 | 0.0 | 0.0 | 0.0 | -0.0886 | None | 3601.6969270706177 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 1.1262 | None | None |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 163080 | 28 | 2159 | 0.0 | 0.0 | None | 3601.6969270706177 | 160921 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2 | 1 | 1 | 0.0 | 0.0 | None | None | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `26`
- Gating Δ: `-67`
- No-generation Δ: `-630861`
- Fast failures Δ: `0`
- Quality changes: `{"LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.1844, "current_avg_pnl": -0.1844, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0886, "current_avg_pnl": -0.0886, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 26, "geometry_changed_delta": 0, "geometry_preserved_delta": 4544, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 3601.7, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
