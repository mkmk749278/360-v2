# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1312` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 325 | 325 | 325 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 2487 | 2487 | 2354 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4321 | 4321 | 4321 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1635705 | 1635380 | 325 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1635705 | 1633218 | 2487 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1635705 | 1631384 | 4321 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1635705 | 1560472 | 75233 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1635705 | 1635700 | 5 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1635705 | 1635705 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 472589 | 472589 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1635705 | 1635705 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1635705 | 1635705 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1635705 | 1632336 | 3369 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1635705 | 1550177 | 85528 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 1635705 | 1503716 | 131989 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1635705 | 1634264 | 1441 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1635705 | 1635687 | 18 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1635705 | 1635705 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 75233 | 75233 | 60294 | 18 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 131989 | 131989 | 105600 | 4 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3369 | 3369 | 2721 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 85528 | 85528 | 36450 | 79 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1441 | 1441 | 1439 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 18 | 18 | 15 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1635380): breakout_not_found=679917, regime_blocked=493809, basic_filters_failed=301172, retest_proximity_failed=151857, volume_spike_missing=8619, missing_fvg_or_orderblock=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1633218): regime_blocked=957411, sweeps_not_detected=223235, basic_filters_failed=211933, ema_alignment_reject=181584, adx_reject=35224, momentum_reject=22879, reclaim_confirmation_failed=837, rsi_reject=115
- **EVAL::DIVERGENCE_CONTINUATION** (total=1631384): regime_blocked=957411, cvd_divergence_failed=371458, basic_filters_failed=211933, cvd_insufficient=36170, retest_proximity_failed=25692, ema_alignment_reject=22089, missing_cvd=6256, missing_fvg_or_orderblock=375
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1560472): auction_not_detected=556676, basic_filters_failed=383968, regime_blocked=369112, reclaim_hold_failed=152783, tail_too_small=97293, rsi_reject=640
- **EVAL::FUNDING_EXTREME** (total=1635700): funding_not_extreme=1102386, basic_filters_failed=440347, missing_funding_rate=39486, ema_alignment_reject=22343, rsi_reject=14093, momentum_reject=13844, cvd_divergence_failed=3201
- **EVAL::LIQUIDATION_REVERSAL** (total=1635705): cascade_threshold_not_met=1158620, basic_filters_failed=451812, cvd_divergence_failed=13459, rsi_reject=11814
- **EVAL::MA_CROSS_TREND_SHIFT** (total=472589): no_ma_cross=335936, basic_filters_failed=136653
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1635705): feature_disabled=1635705
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1635705): regime_blocked=957411, breakout_not_found=249553, basic_filters_failed=211933, ema_alignment_reject=181584, adx_reject=35224
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1632336): regime_blocked=1047406, breakout_not_detected=208712, compression_not_detected=180005, basic_filters_failed=172035, rsi_reject=15401, macd_reject=4659, missing_fvg_or_orderblock=4118
- **EVAL::SR_FLIP_RETEST** (total=1550177): retest_out_of_zone=411872, basic_filters_failed=383968, regime_blocked=369112, flip_close_not_confirmed=231674, reclaim_hold_failed=130542, wick_quality_failed=11356, missing_fvg_or_orderblock=5593, rsi_reject=4745, ema_alignment_reject=1315
- **EVAL::STANDARD** (total=1503716): momentum_reject=458010, basic_filters_failed=392513, adx_reject=271424, ema_alignment_reject=187653, sweeps_not_detected=147576, rsi_reject=37137, macd_reject=8194, invalid_sl_geometry=1209
- **EVAL::TREND_PULLBACK** (total=1634264): regime_blocked=957411, basic_filters_failed=211933, ema_alignment_reject=181584, ema_not_tested_prev=181082, body_conviction_fail=43930, no_ema_reclaim_close=33229, rsi_reject=20346, prev_already_above_emas=2162, prev_already_below_emas=1709, no_prev_high_break=305, no_prev_low_break=296, ema21_not_tagged=276, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1635687): breakout_not_found=525937, regime_blocked=493809, basic_filters_failed=301172, retest_proximity_failed=300951, volume_spike_missing=13495, ema_alignment_reject=316, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=1635705): momentum_reject=1141896, regime_blocked=493809

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 713642 | 37.5% |
| QUIET | 626333 | 32.9% |
| VOLATILE | 476332 | 25.0% |
| TRENDING_DOWN | 86049 | 4.5% |
| RANGING | 59 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **2493**
- Average confidence gap to threshold: **20.33** (samples=2493) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=845, LINKUSDT=438, SOLUSDT=171, XAGUSDT=123, HMSTRUSDT=113, TRXUSDT=113, WLFIUSDT=102, GIGGLEUSDT=92, ONDOUSDT=91, WIFUSDT=84

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 5 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | watchlist_tier_keep | 123 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 12507 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 286 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 951 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 795 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 25373 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 250 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 428 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 612 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 123 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 23412 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1834 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 11242 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 5 | 57.86 | 80.00 | 22.14 | 20.16 | 20.00 | 17.00 | 0.80 | 8.36 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 123 | 53.00 | 50.00 | -3.00 | 22.64 | 20.00 | 17.00 | 0.00 | 8.00 |
| FAILED_AUCTION_RECLAIM | filtered | 12793 | 61.18 | 76.41 | 15.23 | 22.89 | 18.53 | 14.00 | 3.28 | 4.22 |
| FAILED_AUCTION_RECLAIM | kept | 1746 | 63.36 | 56.85 | -6.51 | 23.10 | 19.14 | 14.00 | 3.70 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 25623 | 71.92 | 79.85 | 7.93 | 21.17 | 19.45 | 15.20 | 2.96 | 0.08 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 429 | 66.97 | 64.97 | -2.00 | 21.77 | 19.10 | 15.20 | 5.78 | 0.03 |
| QUIET_COMPRESSION_BREAK | filtered | 735 | 67.51 | 77.49 | 9.98 | 21.79 | 18.58 | 15.82 | 0.00 | 1.51 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 83.20 | 80.00 | -3.20 | 23.20 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 25246 | 54.01 | 77.52 | 23.51 | 20.68 | 19.99 | 15.20 | 1.51 | 3.44 |
| SR_FLIP_RETEST | kept | 11245 | 55.72 | 50.01 | -5.71 | 21.10 | 20.00 | 15.20 | 1.75 | 4.89 |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 80.00 | 1.00 | 21.50 | 17.80 | 18.00 | 5.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 5 | 57.86 | 15.00 | 18.00 | 4.20 | 12.80 | 6.10 | 9.32 | 0.80 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 123 | 53.00 | 15.00 | 18.00 | 3.00 | 10.00 | 5.00 | 10.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 12793 | 61.18 | 24.49 | 14.00 | 3.03 | 10.92 | 5.07 | 5.60 | 3.28 |
| FAILED_AUCTION_RECLAIM | kept | 1746 | 63.36 | 24.62 | 14.00 | 3.16 | 10.57 | 4.84 | 6.18 | 3.70 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 25623 | 71.92 | 24.83 | 14.05 | 3.01 | 12.04 | 8.41 | 6.75 | 2.96 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 429 | 66.97 | 17.02 | 14.01 | 3.00 | 12.00 | 8.49 | 6.71 | 5.78 |
| QUIET_COMPRESSION_BREAK | filtered | 735 | 67.51 | 17.06 | 18.00 | 5.46 | 14.07 | 8.18 | 7.78 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 83.20 | 25.00 | 18.00 | 12.00 | 14.00 | 8.50 | 5.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 25246 | 54.01 | 18.70 | 17.11 | 3.37 | 13.07 | 6.18 | 6.55 | 1.51 |
| SR_FLIP_RETEST | kept | 11245 | 55.72 | 19.83 | 18.00 | 3.00 | 11.11 | 6.65 | 7.62 | 1.75 |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 17.00 | 18.00 | 6.00 | 14.00 | 8.50 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 5 | 57.86 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **0.96** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 123 | 53.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 12793 | 61.18 | 0.00 | 0.00 | 0.01 | 0.00 | 0.02 | 0.00 | **0.03** |
| FAILED_AUCTION_RECLAIM | kept | 1746 | 63.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 25623 | 71.92 | 0.01 | 0.00 | 0.06 | 0.00 | 0.01 | 0.00 | **0.08** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 429 | 66.97 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.03** |
| QUIET_COMPRESSION_BREAK | filtered | 735 | 67.51 | 0.11 | 0.00 | 0.04 | 0.00 | 1.22 | 0.00 | **1.37** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 83.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 25246 | 54.01 | 0.03 | 0.00 | 0.05 | 0.00 | 0.25 | 0.00 | **0.33** |
| SR_FLIP_RETEST | kept | 11245 | 55.72 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **0.96** |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=1 (50.0%) | PREMATURE=0 (0.0%) | NEUTRAL=1 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 1 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| regime_shift | 1 | 0 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| SR_FLIP_RETEST | 1 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8652533`
- `Path funnel` emissions: `261`
- `Regime distribution` emissions: `261`
- `QUIET_SCALP_BLOCK` events: `2493`
- `confidence_gate` events: `77948`
- `free_channel_post` events: `20`
- `pre_tp_fire` events: `1`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **1**
- Avg resolved threshold: **0.200%** raw → avg net **+1.30%** @ 10x
- Avg time-to-fire from dispatch: **32s**
- By threshold source: stamped=1

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 1 | 0.200% | +1.30% | 32 | stamped=1 |
- Top symbols: SOLUSDT=1

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **20**

| Source | Count |
|---|---:|
| regime_shift | 10 |
| signal_close | 9 |
| pre_tp | 1 |

- By severity: HIGH=20

## Dependency readiness
- cvd: presence[absent=31665, present=1604040] state[empty=31665, populated=1604040] buckets[many=735335, none=31665, some=868705] sources[none] quality[none]
- funding_rate: presence[absent=39486, present=1596219] state[empty=39486, populated=1596219] buckets[few=1596219, none=39486] sources[none] quality[none]
- liquidation_clusters: presence[absent=1635705] state[empty=1635705] buckets[none=1635705] sources[none] quality[none]
- oi_snapshot: presence[absent=29486, present=1606219] state[empty=29486, populated=1606219] buckets[few=640, many=1601871, none=29486, some=3708] sources[none] quality[none]
- order_book: presence[absent=86990, present=1548715] state[populated=1548715, unavailable=86990] buckets[few=1548715, none=86990] sources[book_ticker=1548715, unavailable=86990] quality[none=86990, top_of_book_only=1548715]
- orderblocks: presence[absent=1635705] state[empty=1635705] buckets[none=1635705] sources[not_implemented=1635705] quality[none]
- recent_ticks: presence[absent=132770, present=1502935] state[empty=132770, populated=1502935] buckets[many=1502935, none=132770] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.6597784757614136` sec
- Median create→first breach: `32.08602297306061` sec
- Median create→terminal: `33.142032504081726` sec
- Median first breach→terminal: `0.2838468551635742` sec
- Fast-failure buckets: `{"under_120s": {"count": 8, "pct": 100.0}, "under_180s": {"count": 8, "pct": 100.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 8, "pct": 100.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 5 | 5 | 0.0 | 100.0 | 0.0 | -0.8 | 31.312705993652344 | 31.55733895301819 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 100.0 | 0.0 | -0.9575 | 33.25153183937073 | 34.05554413795471 |
| SR_FLIP_RETEST | 2 | 2 | 0.0 | 0.0 | 0.0 | -0.0247 | None | 1130.3681044578552 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 85528 | 79 | 36450 | 0.0 | 0.0 | None | 1130.3681044578552 | 49078 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1441 | 0 | 1439 | 0.0 | 0.0 | None | None | 2 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-17`
- Gating Δ: `-2660`
- No-generation Δ: `1127338`
- Fast failures Δ: `8`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.8, "current_avg_pnl": -0.8, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.9575, "current_avg_pnl": -0.9575, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -17, "geometry_changed_delta": 0, "geometry_preserved_delta": 13319, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 1130.37, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
