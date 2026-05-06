# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT, EVAL::POST_DISPLACEMENT_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::WHALE_MOMENTUM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `22172` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 19 | 19 | 19 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1631296 | 1631284 | 12 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1631296 | 1631290 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1631296 | 1631277 | 19 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1631296 | 1563144 | 68152 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1631296 | 1631295 | 1 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1631296 | 1631296 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1631296 | 1631296 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1631296 | 1631296 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1631296 | 1628556 | 2740 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1631296 | 1550874 | 80422 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1631296 | 1472156 | 159140 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1631296 | 1631293 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1631296 | 1631292 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1631296 | 1631296 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 68152 | 68152 | 62390 | 22 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 159140 | 159140 | 126685 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2740 | 2740 | 2475 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 80422 | 80422 | 45899 | 113 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3 | 3 | 1 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1631284): regime_blocked=800618, breakout_not_found=530701, basic_filters_failed=188012, retest_proximity_failed=110154, volume_spike_missing=1799
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1631290): regime_blocked=1307038, sweeps_not_detected=131541, basic_filters_failed=98528, ema_alignment_reject=68660, adx_reject=18404, momentum_reject=7092, reclaim_confirmation_failed=15, rsi_reject=12
- **EVAL::DIVERGENCE_CONTINUATION** (total=1631277): regime_blocked=1307038, cvd_divergence_failed=191287, basic_filters_failed=98528, missing_cvd=16684, cvd_insufficient=7656, ema_alignment_reject=5395, retest_proximity_failed=4667, missing_fvg_or_orderblock=22
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1563144): regime_blocked=506379, auction_not_detected=464824, basic_filters_failed=364362, reclaim_hold_failed=136425, tail_too_small=90214, rsi_reject=940
- **EVAL::FUNDING_EXTREME** (total=1631295): funding_not_extreme=1108190, basic_filters_failed=443651, missing_funding_rate=36885, ema_alignment_reject=21437, momentum_reject=9427, rsi_reject=9229, cvd_divergence_failed=2476
- **EVAL::LIQUIDATION_REVERSAL** (total=1631296): cascade_threshold_not_met=1135129, basic_filters_failed=453841, cvd_divergence_failed=31424, rsi_reject=10901, missing_cvd=1
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1631296): feature_disabled=1631296
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1631296): regime_blocked=1307038, breakout_not_found=138666, basic_filters_failed=98528, ema_alignment_reject=68660, adx_reject=18404
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1628556): regime_blocked=830637, breakout_not_detected=281791, basic_filters_failed=265834, compression_not_detected=230033, rsi_reject=13027, missing_fvg_or_orderblock=4782, macd_reject=2452
- **EVAL::SR_FLIP_RETEST** (total=1550874): regime_blocked=506379, basic_filters_failed=364362, retest_out_of_zone=341914, flip_close_not_confirmed=180039, reclaim_hold_failed=121087, wick_quality_failed=15726, missing_fvg_or_orderblock=11724, rsi_reject=8117, ema_alignment_reject=1526
- **EVAL::STANDARD** (total=1472156): momentum_reject=463533, basic_filters_failed=415407, adx_reject=249310, ema_alignment_reject=150570, sweeps_not_detected=140288, rsi_reject=41862, macd_reject=10729, invalid_sl_geometry=457
- **EVAL::TREND_PULLBACK** (total=1631293): regime_blocked=1307038, ema_not_tested_prev=102898, basic_filters_failed=98528, ema_alignment_reject=68660, no_ema_reclaim_close=25484, body_conviction_fail=20409, rsi_reject=5513, prev_already_above_emas=2739, no_prev_high_break=16, prev_already_below_emas=4, no_prev_low_break=2, ema21_not_tagged=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1631292): regime_blocked=800618, breakout_not_found=407122, retest_proximity_failed=224587, basic_filters_failed=188012, volume_spike_missing=10637, ema_alignment_reject=316
- **EVAL::WHALE_MOMENTUM** (total=1631296): momentum_reject=830678, regime_blocked=800618

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 871283 | 45.2% |
| VOLATILE | 654511 | 34.0% |
| TRENDING_UP | 401736 | 20.8% |
| TRENDING_DOWN | 154 | 0.0% |
| RANGING | 51 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **4578**
- Average confidence gap to threshold: **20.27** (samples=4578) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=1342, LINKUSDT=637, ONDOUSDT=295, GIGGLEUSDT=295, WLFIUSDT=281, HMSTRUSDT=277, TRXUSDT=172, XAGUSDT=171, SOLUSDT=158, NOTUSDT=126

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | watchlist_tier_keep | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 3020 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 634 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 1925 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 31528 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 488 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 240 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 37 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 6737 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3216 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 16841 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 53.00 | 50.00 | -3.00 | 22.70 | 20.00 | 17.00 | 0.00 | 8.00 |
| FAILED_AUCTION_RECLAIM | filtered | 3654 | 60.71 | 77.40 | 16.69 | 21.98 | 19.25 | 14.00 | 3.21 | 1.03 |
| FAILED_AUCTION_RECLAIM | kept | 1927 | 50.83 | 50.03 | -0.80 | 23.15 | 18.13 | 14.00 | 1.13 | 5.56 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 32016 | 71.78 | 79.77 | 7.99 | 21.12 | 19.47 | 15.20 | 2.96 | 0.16 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 58.30 | 50.00 | -8.30 | 23.90 | 19.90 | 15.20 | 0.00 | 12.00 |
| QUIET_COMPRESSION_BREAK | filtered | 277 | 50.73 | 67.00 | 16.27 | 20.79 | 18.36 | 15.80 | 0.00 | 8.63 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 83.20 | 80.00 | -3.20 | 23.20 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 9953 | 48.92 | 75.15 | 26.23 | 20.14 | 19.99 | 15.21 | 1.42 | 2.41 |
| SR_FLIP_RETEST | kept | 16842 | 57.25 | 50.00 | -7.25 | 21.05 | 20.00 | 15.20 | 1.75 | 6.25 |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 80.00 | 1.00 | 21.50 | 17.80 | 18.00 | 5.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 53.00 | 15.00 | 18.00 | 3.00 | 10.00 | 5.00 | 10.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 3654 | 60.71 | 21.35 | 14.00 | 4.25 | 12.74 | 5.28 | 5.67 | 3.21 |
| FAILED_AUCTION_RECLAIM | kept | 1927 | 50.83 | 17.61 | 14.00 | 3.01 | 11.39 | 4.84 | 5.49 | 1.13 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 32016 | 71.78 | 24.80 | 14.04 | 3.01 | 12.05 | 8.37 | 6.76 | 2.96 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 58.30 | 25.00 | 18.00 | 3.00 | 10.00 | 5.00 | 9.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 277 | 50.73 | 18.87 | 18.00 | 5.48 | 14.95 | 5.46 | 6.01 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 83.20 | 25.00 | 18.00 | 12.00 | 14.00 | 8.50 | 5.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 9953 | 48.92 | 19.04 | 14.34 | 3.86 | 15.11 | 5.03 | 4.72 | 1.42 |
| SR_FLIP_RETEST | kept | 16842 | 57.25 | 19.84 | 18.00 | 3.00 | 11.07 | 6.69 | 8.32 | 1.75 |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 17.00 | 18.00 | 6.00 | 14.00 | 8.50 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 53.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 3654 | 60.71 | 0.00 | 0.00 | 0.02 | 0.00 | 0.10 | 0.00 | **0.12** |
| FAILED_AUCTION_RECLAIM | kept | 1927 | 50.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 32016 | 71.78 | 0.00 | 0.00 | 0.15 | 0.00 | 0.01 | 0.00 | **0.16** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 58.30 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| QUIET_COMPRESSION_BREAK | filtered | 277 | 50.73 | 0.49 | 0.00 | 0.05 | 0.00 | 6.34 | 0.00 | **6.88** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 83.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 9953 | 48.92 | 0.08 | 0.00 | 0.17 | 0.00 | 0.53 | 0.00 | **0.78** |
| SR_FLIP_RETEST | kept | 16842 | 57.25 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | **0.41** |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=5 (38.5%) | PREMATURE=0 (0.0%) | NEUTRAL=8 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 5 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 5 | 0 | 8 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 2 | 0 | 3 | 0 |
| SR_FLIP_RETEST | 3 | 0 | 3 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8164275`
- `Path funnel` emissions: `264`
- `Regime distribution` emissions: `264`
- `QUIET_SCALP_BLOCK` events: `4578`
- `confidence_gate` events: `64674`
- `free_channel_post` events: `6`
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
- Total posts in window: **6**

| Source | Count |
|---|---:|
| regime_shift | 5 |
| pre_tp | 1 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[absent=70911, present=1560385] state[empty=70911, populated=1560385] buckets[few=3, many=617957, none=70911, some=942425] sources[none] quality[none]
- funding_rate: presence[absent=36885, present=1594411] state[empty=36885, populated=1594411] buckets[few=1594411, none=36885] sources[none] quality[none]
- liquidation_clusters: presence[absent=1631296] state[empty=1631296] buckets[none=1631296] sources[none] quality[none]
- oi_snapshot: presence[absent=29457, present=1601839] state[empty=29457, populated=1601839] buckets[few=640, many=1597491, none=29457, some=3708] sources[none] quality[none]
- order_book: presence[absent=91871, present=1539425] state[populated=1539425, unavailable=91871] buckets[few=1539425, none=91871] sources[book_ticker=1539425, unavailable=91871] quality[none=91871, top_of_book_only=1539425]
- orderblocks: presence[absent=1631296] state[empty=1631296] buckets[none=1631296] sources[not_implemented=1631296] quality[none]
- recent_ticks: presence[absent=128452, present=1502844] state[empty=128452, populated=1502844] buckets[many=1502844, none=128452] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.80971097946167` sec
- Median create→first breach: `None` sec
- Median create→terminal: `610.247466802597` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0122 | None | 609.7865469455719 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0682 | None | 908.4312560558319 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 80422 | 113 | 45899 | 0.0 | 0.0 | None | None | 34523 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3 | 0 | 1 | 0.0 | 0.0 | None | None | 2 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-34`
- Gating Δ: `51134`
- No-generation Δ: `546849`
- Fast failures Δ: `-1`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": 0.1748, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.1748, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": -5270, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -643.44, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -49.19, "median_terminal_delta_sec": -49.41, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::WHALE_MOMENTUM**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **EVAL::WHALE_MOMENTUM**
