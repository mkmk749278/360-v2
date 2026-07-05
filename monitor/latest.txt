# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION
- Top promising signals/paths: SR_FLIP_RETEST
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `694` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 67 | 67 | 67 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1504 | 1504 | 1207 | 3 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 27380 | 27373 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 22549 | 22549 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 22536 | 21995 | 554 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 22551 | 21934 | 640 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 27415 | 27258 | 163 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 21468 | 21469 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 22575 | 22575 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 31688 | 32008 | 1519 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 27382 | 18837 | 12848 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 27013 | 27014 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 22550 | 22546 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 22532 | 22529 | 7 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 22129 | 20150 | 2376 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 17537 | 16012 | 1570 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 17582 | 17528 | 60 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 27376 | 27372 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 21469 | 21471 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1993 | 1993 | 1623 | 5 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 301 | 301 | 234 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 6407 | 6407 | 6406 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3327 | 3327 | 3327 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 27622 | 27622 | 27132 | 3 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 14 | 14 | 13 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 40 | 40 | 40 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 6962 | 6962 | 6475 | 2 | active-healthy (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 188 | 188 | 188 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 36 | 36 | 0 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=27373): breakout_not_found=10988, basic_filters_failed=9192, move_not_fresh=5285, breakout_stale=1535, retest_proximity_failed=299, volume_spike_missing=74
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=22549): cls_disabled_merged_into_lsr=22549
- **EVAL::DIVERGENCE_CONTINUATION** (total=21995): h1_trend_not_aligned=9740, basic_filters_failed=5533, cvd_divergence_failed=4517, ema_alignment_reject=1585, retest_proximity_failed=559, missing_fvg_or_orderblock=61
- **EVAL::FAILED_AUCTION_RECLAIM** (total=21934): auction_not_detected=7338, basic_filters_failed=5318, reclaim_hold_failed=4717, tail_too_small=3439, regime_blocked=1122
- **EVAL::FUNDING_EXTREME** (total=27258): funding_not_extreme=19000, basic_filters_failed=6574, ema_alignment_reject=815, rsi_reject=292, missing_funding_rate=272, cvd_divergence_failed=170, momentum_reject=97, missing_fvg_or_orderblock=38
- **EVAL::LIQUIDATION_REVERSAL** (total=21469): cascade_threshold_not_met=14628, basic_filters_failed=6618, rsi_reject=120, cvd_divergence_failed=98, volume_spike_missing=3, missing_fvg_or_orderblock=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=22575): no_ma_cross=16121, basic_filters_failed=5535, ma_cross_cooldown=616, ma_cross_htf_misaligned=303
- **EVAL::MOVER_AVWAP_SCALP** (total=32008): no_avwap_tag=18146, basic_filters_failed=9201, no_mover_leg=2481, avwap_slope_against=1159, avwap_reclaim_no_volume=857, no_avwap_reclaim=164
- **EVAL::MOVER_TREND_PULLBACK** (total=18837): basic_filters_failed=9198, mover_run_too_small=4984, no_reclaim=3309, no_pullback_tag=1346
- **EVAL::OPENING_RANGE_BREAKOUT** (total=27014): feature_disabled=27014
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=22546): regime_blocked=16701, breakout_not_found=4053, basic_filters_failed=1299, adx_reject=490, ema_alignment_reject=3
- **EVAL::QUIET_COMPRESSION_BREAK** (total=22529): compression_not_detected=11237, regime_blocked=6967, basic_filters_failed=4019, breakout_not_detected=300, volume_confirmation_failed=6
- **EVAL::SR_FLIP_RETEST** (total=20150): basic_filters_failed=5316, flip_close_not_confirmed=3690, reclaim_hold_failed=2785, whipsaw_flip=2367, long_break_volume_thin=1898, retest_out_of_zone=1813, regime_blocked=1119, wick_quality_failed=533, long_disabled=467, missing_fvg_or_orderblock=92, long_acceptance_not_held=54, ema_alignment_reject=16
- **EVAL::STANDARD** (total=16012): momentum_reject=5079, sweeps_not_detected=2936, adx_reject=2608, basic_filters_failed=2548, macd_reject=1966, ema_alignment_reject=814, invalid_sl_geometry=55, rsi_reject=6
- **EVAL::TREND_PULLBACK** (total=17528): h1_trend_not_aligned=10307, ema_alignment_reject=2178, h1_pullback_not_confirmed=1773, basic_filters_failed=1400, ema_not_tested_prev=911, no_ema_reclaim_close=441, rsi_reject=143, body_conviction_fail=110, prev_already_above_emas=109, no_prev_high_break=61, prev_already_below_emas=35, momentum_flat=27, no_prev_low_break=22, ema21_not_tagged=11
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=27372): breakout_not_found=15501, basic_filters_failed=9192, move_not_fresh=1305, breakout_stale=823, retest_proximity_failed=319, volume_spike_missing=227, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=21471): momentum_reject=15540, recent_ticks_insufficient=4488, basic_filters_failed=1443

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 60178 | 48.1% |
| QUIET | 26189 | 20.9% |
| TRENDING_DOWN | 18544 | 14.8% |
| TRENDING_UP | 11516 | 9.2% |
| VOLATILE | 8643 | 6.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **11**
- Average confidence gap to threshold: **21.36** (samples=11) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 73 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 110 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 25 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 51 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 73 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 35 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 60.05 | 65.00 | 4.95 | 23.37 | 19.40 | 17.00 | -0.95 | 6.00 |
| DIVERGENCE_CONTINUATION | kept | 73 | 72.48 | 65.00 | -7.48 | 18.65 | 19.30 | 19.47 | 2.51 | -2.88 |
| FAILED_AUCTION_RECLAIM | filtered | 110 | 51.25 | 65.00 | 13.75 | 20.76 | 19.87 | 20.00 | 4.29 | 4.26 |
| FAILED_AUCTION_RECLAIM | kept | 25 | 71.53 | 65.00 | -6.53 | 20.76 | 19.66 | 20.00 | 4.74 | 2.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 71.70 | 65.00 | -6.70 | 21.20 | 19.80 | 20.00 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 51 | 75.91 | 65.00 | -10.91 | 20.35 | 19.04 | 15.80 | 5.07 | 0.00 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 80.00 | 65.00 | -15.00 | 20.60 | 20.00 | 20.00 | 4.50 | 0.00 |
| SR_FLIP_RETEST | filtered | 84 | 52.15 | 65.00 | 12.85 | 22.93 | 20.00 | 16.08 | 1.90 | 18.72 |
| SR_FLIP_RETEST | kept | 2 | 68.60 | 65.00 | -3.60 | 22.65 | 20.00 | 15.20 | 2.50 | 4.75 |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 62.50 | 65.00 | 2.50 | 18.35 | 18.10 | 20.00 | 4.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 87.00 | 65.00 | -22.00 | 21.20 | 17.60 | 20.00 | 6.00 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 60.05 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | -0.95 |
| DIVERGENCE_CONTINUATION | kept | 73 | 72.48 | 19.52 | 15.26 | 7.48 | 10.99 | 7.33 | 9.48 | 2.51 |
| FAILED_AUCTION_RECLAIM | filtered | 110 | 51.25 | 20.04 | 18.00 | 3.57 | 14.81 | 6.25 | 3.55 | 4.29 |
| FAILED_AUCTION_RECLAIM | kept | 25 | 71.53 | 23.40 | 15.28 | 5.52 | 12.12 | 5.90 | 7.57 | 4.74 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 71.70 | 25.00 | 14.00 | 3.00 | 12.00 | 9.00 | 5.70 | 3.00 |
| MOVER_TREND_PULLBACK | kept | 51 | 75.91 | 18.57 | 18.00 | 7.88 | 10.80 | 6.51 | 9.07 | 5.07 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 80.00 | 17.00 | 18.00 | 15.00 | 11.00 | 8.50 | 6.00 | 4.50 |
| SR_FLIP_RETEST | filtered | 84 | 52.15 | 20.62 | 16.69 | 6.25 | 13.32 | 6.95 | 5.14 | 1.90 |
| SR_FLIP_RETEST | kept | 2 | 68.60 | 25.00 | 18.00 | 3.00 | 12.50 | 6.50 | 5.85 | 2.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 62.50 | 2.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 87.00 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 6.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 60.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 73 | 72.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 110 | 51.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 25 | 71.53 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **2.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 71.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 51 | 75.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 80.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 84 | 52.15 | 0.00 | 0.00 | 0.00 | 0.00 | 6.46 | 0.00 | 0.00 | 1.41 | **7.87** |
| SR_FLIP_RETEST | kept | 2 | 68.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 62.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 87.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=100 (68.5%) | PREMATURE=16 (11.0%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 84 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 100 | 16 | 30 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 6 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 25 | 6 | 11 | 0 |
| FUNDING_EXTREME_SIGNAL | 0 | 1 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 2 | 3 | 0 |
| MOVER_AVWAP_SCALP | 10 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 27 | 2 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 20 | 5 | 10 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 100 | 16 | 30 | 71.5 | 29.9 | +0.28 | **KEEP** — net-helping: avg +0.28R/kill across 146 kills (saved 71.5R vs missed 29.9R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `48213`
- `Path funnel` emissions: `14`
- `Regime distribution` emissions: `14`
- `QUIET_SCALP_BLOCK` events: `11`
- `confidence_gate` events: `402`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| signal_close | 5 |
| regime_shift | 1 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=95158] state[populated=95158] buckets[many=95158] sources[none] quality[none]
- funding_rate: presence[absent=13381, present=81777] state[empty=13381, populated=81777] buckets[few=81777, none=13381] sources[none] quality[none]
- liquidation_clusters: presence[absent=54070, present=41088] state[empty=54070, populated=41088] buckets[few=33598, none=54070, some=7490] sources[none] quality[none]
- oi_snapshot: presence[absent=12786, present=82372] state[empty=12786, populated=82372] buckets[many=82372, none=12786] sources[none] quality[none]
- order_book: presence[absent=26941, present=68217] state[populated=68217, unavailable=26941] buckets[few=68217, none=26941] sources[book_ticker=68217, unavailable=26941] quality[none=26941, top_of_book_only=68217]
- orderblocks: presence[absent=95158] state[empty=95158] buckets[none=95158] sources[not_implemented=95158] quality[none]
- recent_ticks: presence[present=95158] state[populated=95158] buckets[many=95158] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.938218116760254` sec
- Median create→first breach: `943.7224609851837` sec
- Median create→terminal: `2306.390836954117` sec
- Median first breach→terminal: `2.87716007232666` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 3.4}, "under_180s": {"count": 2, "pct": 6.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 4.3}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 8 | 25.0 | 50.0 | 25.0 | 0.0 | -0.033 | 841.1757040023804 | 863.2891384363174 |
| FAILED_AUCTION_RECLAIM | 15 | 15 | 20.0 | 6.7 | 20.0 | 0.0 | 1.1192 | 1596.742919921875 | 3602.2941648960114 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.9824 | 374.2138681411743 | 376.2545499801636 |
| MOVER_TREND_PULLBACK | 11 | 11 | 0.0 | 27.3 | 0.0 | 0.0 | 0.1436 | 1786.3923320770264 | 2669.9846189022064 |
| SR_FLIP_RETEST | 6 | 6 | 50.0 | 33.3 | 50.0 | 0.0 | 0.0977 | 396.0454330444336 | 423.18594098091125 |
| VOLUME_SURGE_BREAKOUT | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -0.5768 | 220.4893138408661 | 1691.334305047989 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 6962 | 2 | 6475 | 50.0 | 33.3 | 396.0454330444336 | 423.18594098091125 | 487 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 188 | 0 | 188 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `16`
- Gating Δ: `46712`
- No-generation Δ: `390620`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.6289, "current_avg_pnl": -0.033, "current_win_rate": 25.0, "previous_avg_pnl": -0.6619, "previous_win_rate": 0.0, "win_rate_delta": 25.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.8429, "current_avg_pnl": 1.1192, "current_win_rate": 20.0, "previous_avg_pnl": 0.2763, "previous_win_rate": 16.7, "win_rate_delta": 3.3}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -1.2408, "current_avg_pnl": -0.9824, "current_win_rate": 0.0, "previous_avg_pnl": 0.2584, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.4979, "current_avg_pnl": 0.1436, "current_win_rate": 0.0, "previous_avg_pnl": -0.3543, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.2657, "current_avg_pnl": 0.0977, "current_win_rate": 50.0, "previous_avg_pnl": 0.3634, "previous_win_rate": 0.0, "win_rate_delta": 50.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -0.5768, "current_avg_pnl": -0.5768, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 487, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -564.54, "median_terminal_delta_sec": -3190.03, "sl_rate_delta": 33.3, "win_rate_delta": 50.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -315.23, "median_terminal_delta_sec": -317.09, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **SR_FLIP_RETEST**
- Most likely bottleneck: **MOVER_AVWAP_SCALP**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
