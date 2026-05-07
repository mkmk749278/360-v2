# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1278` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 26 | 26 | 19 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 5572 | 5572 | 5273 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1767 | 1767 | 1766 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1369168 | 1369142 | 26 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1369168 | 1363596 | 5572 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1369168 | 1367401 | 1767 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1369168 | 1289539 | 79629 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1369168 | 1369168 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1369168 | 1369168 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1369168 | 1369168 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1369168 | 1369168 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1369168 | 1369168 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1369168 | 1358063 | 11105 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1369168 | 1286488 | 82680 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1369168 | 1300649 | 68519 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 1369168 | 1366309 | 2859 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1369168 | 1368887 | 281 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1369168 | 1369168 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 79629 | 79629 | 43663 | 23 | active-low-quality (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 68519 | 68519 | 56624 | 9 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 11105 | 11105 | 2664 | 20 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 82680 | 82680 | 10655 | 30 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2859 | 2859 | 2852 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 281 | 281 | 9 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1369142): breakout_not_found=767956, basic_filters_failed=435746, retest_proximity_failed=154792, volume_spike_missing=10373, missing_fvg_or_orderblock=275
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1363596): regime_blocked=550809, sweeps_not_detected=272605, ema_alignment_reject=249028, basic_filters_failed=240219, adx_reject=42942, momentum_reject=7429, reclaim_confirmation_failed=458, rsi_reject=106
- **EVAL::DIVERGENCE_CONTINUATION** (total=1367401): regime_blocked=550809, cvd_divergence_failed=469581, basic_filters_failed=240219, retest_proximity_failed=44185, ema_alignment_reject=30137, cvd_insufficient=27632, missing_cvd=4837, missing_fvg_or_orderblock=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1289539): auction_not_detected=551128, basic_filters_failed=428079, reclaim_hold_failed=152743, tail_too_small=102289, regime_blocked=54494, rsi_reject=806
- **EVAL::FUNDING_EXTREME** (total=1369168): funding_not_extreme=911763, basic_filters_failed=433766, ema_alignment_reject=7840, rsi_reject=7800, missing_funding_rate=5482, momentum_reject=1861, cvd_divergence_failed=656
- **EVAL::LIQUIDATION_REVERSAL** (total=1369168): cascade_threshold_not_met=930134, basic_filters_failed=435746, cvd_divergence_failed=2841, rsi_reject=446, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1369168): no_ma_cross=933422, basic_filters_failed=435746
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1369168): feature_disabled=1369168
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1369168): regime_blocked=550809, breakout_not_found=286170, ema_alignment_reject=249028, basic_filters_failed=240219, adx_reject=42942
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1358063): regime_blocked=872853, basic_filters_failed=187860, breakout_not_detected=167599, compression_not_detected=106563, rsi_reject=14619, macd_reject=5864, missing_fvg_or_orderblock=2705
- **EVAL::SR_FLIP_RETEST** (total=1286488): basic_filters_failed=428079, retest_out_of_zone=396867, flip_close_not_confirmed=229912, reclaim_hold_failed=151429, regime_blocked=54494, wick_quality_failed=11859, rsi_reject=6559, missing_fvg_or_orderblock=5383, ema_alignment_reject=1906
- **EVAL::STANDARD** (total=1300649): basic_filters_failed=368704, momentum_reject=284161, adx_reject=269307, sweeps_not_detected=191200, ema_alignment_reject=153960, macd_reject=14307, invalid_sl_geometry=9512, rsi_reject=9498
- **EVAL::TREND_PULLBACK** (total=1366309): regime_blocked=550809, ema_alignment_reject=249028, basic_filters_failed=240219, ema_not_tested_prev=227324, body_conviction_fail=52900, rsi_reject=21702, no_ema_reclaim_close=18848, prev_already_above_emas=2943, prev_already_below_emas=1279, no_prev_high_break=1116, no_prev_low_break=132, ema21_not_tagged=9
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1368887): breakout_not_found=599506, basic_filters_failed=435746, retest_proximity_failed=309216, volume_spike_missing=24418, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=1369168): momentum_reject=1369168

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 937411 | 55.0% |
| QUIET | 591278 | 34.7% |
| TRENDING_DOWN | 70218 | 4.1% |
| VOLATILE | 64714 | 3.8% |
| RANGING | 39229 | 2.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **697**
- Average confidence gap to threshold: **7.98** (samples=697) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=320, WIFUSDT=317, TONUSDT=17, XAUUSDT=14, XAGUSDT=6, BTCUSDT=5, ETHUSDT=5, SOLUSDT=4, ZECUSDT=3, CLUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 8 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 15038 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 358 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 11891 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 284 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 10094 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 323 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6122 |
| SR_FLIP_RETEST | filtered | min_confidence | 21446 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 454 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 271 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 8 | 56.30 | 65.00 | 8.70 | 23.04 | 20.00 | 17.00 | 0.00 | -3.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 72.00 | 65.00 | -7.00 | 20.10 | 20.00 | 17.00 | 0.00 | -3.00 |
| FAILED_AUCTION_RECLAIM | filtered | 15396 | 60.50 | 65.00 | 4.50 | 23.04 | 18.06 | 14.00 | 3.53 | 5.93 |
| FAILED_AUCTION_RECLAIM | kept | 11891 | 68.07 | 65.00 | -3.07 | 22.91 | 20.00 | 14.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 289 | 54.00 | 65.00 | 11.00 | 23.99 | 17.46 | 15.20 | 0.09 | 11.87 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10094 | 66.39 | 65.00 | -1.39 | 21.76 | 19.10 | 15.20 | 5.16 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 323 | 54.72 | 65.00 | 10.28 | 20.99 | 19.70 | 15.80 | 0.00 | 4.25 |
| QUIET_COMPRESSION_BREAK | kept | 6122 | 73.78 | 65.00 | -8.78 | 20.87 | 18.13 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 21457 | 57.29 | 65.00 | 7.71 | 21.99 | 19.99 | 15.20 | 1.19 | 7.28 |
| SR_FLIP_RETEST | kept | 454 | 67.60 | 65.00 | -2.60 | 21.96 | 20.00 | 15.22 | 1.35 | 2.73 |
| VOLUME_SURGE_BREAKOUT | filtered | 271 | 55.50 | 65.00 | 9.50 | 24.03 | 16.60 | 20.00 | 1.50 | 12.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 8 | 56.30 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 6.30 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 72.00 | 25.00 | 18.00 | 3.00 | 11.00 | 5.00 | 10.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 15396 | 60.50 | 24.86 | 14.04 | 3.07 | 11.06 | 5.00 | 5.32 | 3.53 |
| FAILED_AUCTION_RECLAIM | kept | 11891 | 68.07 | 25.00 | 14.28 | 3.05 | 8.99 | 5.02 | 6.72 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 289 | 54.00 | 17.11 | 19.85 | 3.05 | 11.19 | 4.95 | 9.89 | 0.09 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10094 | 66.39 | 17.00 | 14.00 | 3.00 | 12.00 | 8.50 | 6.70 | 5.16 |
| QUIET_COMPRESSION_BREAK | filtered | 323 | 54.72 | 17.15 | 18.00 | 11.72 | 14.06 | 8.40 | 4.46 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6122 | 73.78 | 24.26 | 17.50 | 3.27 | 14.27 | 8.62 | 5.85 | 0.00 |
| SR_FLIP_RETEST | filtered | 21457 | 57.29 | 16.03 | 17.99 | 3.48 | 11.86 | 7.77 | 8.95 | 1.19 |
| SR_FLIP_RETEST | kept | 454 | 67.60 | 18.81 | 18.00 | 3.63 | 15.03 | 5.08 | 8.97 | 1.35 |
| VOLUME_SURGE_BREAKOUT | filtered | 271 | 55.50 | 17.00 | 20.00 | 3.00 | 11.00 | 5.00 | 10.00 | 1.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 8 | 56.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 15396 | 60.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | **0.01** |
| FAILED_AUCTION_RECLAIM | kept | 11891 | 68.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 289 | 54.00 | 0.00 | 0.00 | 11.79 | 0.00 | 0.07 | 0.00 | **11.86** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10094 | 66.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 323 | 54.72 | 0.00 | 0.00 | 0.04 | 0.00 | 4.15 | 0.00 | **4.19** |
| QUIET_COMPRESSION_BREAK | kept | 6122 | 73.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 21457 | 57.29 | 0.00 | 0.00 | 0.31 | 0.00 | 0.01 | 0.00 | **0.32** |
| SR_FLIP_RETEST | kept | 454 | 67.60 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.02** |
| VOLUME_SURGE_BREAKOUT | filtered | 271 | 55.50 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=12 (80.0%) | PREMATURE=0 (0.0%) | NEUTRAL=3 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 12 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 3 | 0 | 1 | 0 |
| other | 2 | 0 | 1 | 0 |
| regime_shift | 7 | 0 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 0 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 7 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 4 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8538674`
- `Path funnel` emissions: `229`
- `Regime distribution` emissions: `229`
- `QUIET_SCALP_BLOCK` events: `697`
- `confidence_gate` events: `66306`
- `free_channel_post` events: `37`
- `pre_tp_fire` events: `11`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **11**
- Avg resolved threshold: **0.386%** raw → avg net **+3.16%** @ 10x
- Avg time-to-fire from dispatch: **656s**
- By threshold source: stamped=11

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 7 | 0.200% | +1.30% | 747 | stamped=7 |
| QUIET_COMPRESSION_BREAK | 2 | 0.513% | +4.42% | 432 | stamped=2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1.503% | +14.33% | 212 | stamped=1 |
| FAILED_AUCTION_RECLAIM | 1 | 0.319% | +2.49% | 910 | stamped=1 |
- Top symbols: SOLUSDT=2, CLUSDT=2, BTCUSDT=2, DOGEUSDT=1, TONUSDT=1, LABUSDT=1, XRPUSDT=1, ZECUSDT=1

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **37**

| Source | Count |
|---|---:|
| signal_close | 24 |
| pre_tp | 11 |
| regime_shift | 2 |

- By severity: HIGH=37

## Dependency readiness
- cvd: presence[absent=22809, present=1346359] state[empty=22809, populated=1346359] buckets[many=1072892, none=22809, some=273467] sources[none] quality[none]
- funding_rate: presence[absent=5482, present=1363686] state[empty=5482, populated=1363686] buckets[few=1363686, none=5482] sources[none] quality[none]
- liquidation_clusters: presence[absent=1369168] state[empty=1369168] buckets[none=1369168] sources[none] quality[none]
- oi_snapshot: presence[absent=208, present=1368960] state[empty=208, populated=1368960] buckets[few=187, many=1367684, none=208, some=1089] sources[none] quality[none]
- order_book: presence[absent=66294, present=1302874] state[populated=1302874, unavailable=66294] buckets[few=1302874, none=66294] sources[book_ticker=1302874, unavailable=66294] quality[none=66294, top_of_book_only=1302874]
- orderblocks: presence[absent=1369168] state[empty=1369168] buckets[none=1369168] sources[not_implemented=1369168] quality[none]
- recent_ticks: presence[absent=100405, present=1268763] state[empty=100405, populated=1268763] buckets[many=1268763, none=100405] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.0527560710906982` sec
- Median create→first breach: `882.0779721736908` sec
- Median create→terminal: `658.8001929521561` sec
- Median first breach→terminal: `2.545747995376587` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 14.3}, "under_180s": {"count": 1, "pct": 14.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0113 | None | 609.8221759796143 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.35 | 896.6341761350632 | 1803.5976575613022 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 33.3 | 0.0 | -0.5167 | 380.06766152381897 | 381.7530280351639 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 0.0 | 0.0 | 0.0 | -0.1206 | 835.6122620105743 | 611.0443550348282 |
| SR_FLIP_RETEST | 12 | 12 | 0.0 | 0.0 | 0.0 | 0.1961 | 1325.9992390871048 | 890.0644371509552 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 82680 | 30 | 10655 | 0.0 | 0.0 | 1325.9992390871048 | 890.0644371509552 | 72025 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2859 | 0 | 2852 | 0.0 | 0.0 | None | None | 7 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-20`
- Gating Δ: `-91100`
- No-generation Δ: `-2868357`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.35, "current_avg_pnl": 0.35, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.5167, "current_avg_pnl": -0.5167, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1206, "current_avg_pnl": -0.1206, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1961, "current_avg_pnl": 0.1961, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -49, "geometry_changed_delta": 0, "geometry_preserved_delta": 22831, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1326.0, "median_terminal_delta_sec": 890.06, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **TREND_PULLBACK_EMA**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
