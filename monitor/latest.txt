# Runtime Truth Report

## Executive summary
- Overall health/freshness: **unhealthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=unhealthy)
- Heartbeat age: `9310` sec (warning=True)
- Latest performance record age: `9672` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 323 | 323 | 323 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 5560 | 5560 | 5405 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4386 | 4386 | 4386 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1398749 | 1398426 | 323 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1398749 | 1393189 | 5560 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1398749 | 1394363 | 4386 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1398749 | 1325205 | 73544 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1398749 | 1398744 | 5 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1398749 | 1398749 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 930144 | 930144 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1398749 | 1398749 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1398749 | 1398749 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1398749 | 1396448 | 2301 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1398749 | 1319684 | 79065 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 1398749 | 1330800 | 67949 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1398749 | 1395570 | 3179 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1398749 | 1398731 | 18 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1398749 | 1398749 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 73544 | 73544 | 49286 | 27 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 67949 | 67949 | 55696 | 8 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2301 | 2301 | 1639 | 4 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 79065 | 79065 | 19742 | 47 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3179 | 3179 | 3177 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 18 | 18 | 15 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1398426): breakout_not_found=728449, basic_filters_failed=349681, regime_blocked=162695, retest_proximity_failed=146236, volume_spike_missing=11359, missing_fvg_or_orderblock=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1393189): regime_blocked=469755, sweeps_not_detected=298289, basic_filters_failed=277924, ema_alignment_reject=271200, adx_reject=52291, momentum_reject=22612, reclaim_confirmation_failed=954, rsi_reject=164
- **EVAL::DIVERGENCE_CONTINUATION** (total=1394363): cvd_divergence_failed=521377, regime_blocked=469755, basic_filters_failed=277924, retest_proximity_failed=44806, cvd_insufficient=41778, ema_alignment_reject=32490, missing_cvd=5858, missing_fvg_or_orderblock=375
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1325205): auction_not_detected=580008, basic_filters_failed=372470, reclaim_hold_failed=150957, regime_blocked=123400, tail_too_small=97683, rsi_reject=687
- **EVAL::FUNDING_EXTREME** (total=1398744): funding_not_extreme=956334, basic_filters_failed=394851, ema_alignment_reject=13680, rsi_reject=11722, momentum_reject=10474, missing_funding_rate=10061, cvd_divergence_failed=1622
- **EVAL::LIQUIDATION_REVERSAL** (total=1398749): cascade_threshold_not_met=990615, basic_filters_failed=398205, rsi_reject=5364, cvd_divergence_failed=4565
- **EVAL::MA_CROSS_TREND_SHIFT** (total=930144): no_ma_cross=663080, basic_filters_failed=267064
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1398749): feature_disabled=1398749
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1398749): regime_blocked=469755, breakout_not_found=327579, basic_filters_failed=277924, ema_alignment_reject=271200, adx_reject=52291
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1396448): regime_blocked=1052394, breakout_not_detected=135342, basic_filters_failed=94546, compression_not_detected=89723, rsi_reject=15834, macd_reject=4859, missing_fvg_or_orderblock=3750
- **EVAL::SR_FLIP_RETEST** (total=1319684): retest_out_of_zone=414730, basic_filters_failed=372470, flip_close_not_confirmed=250640, reclaim_hold_failed=139767, regime_blocked=123400, wick_quality_failed=10332, rsi_reject=5325, ema_alignment_reject=1586, missing_fvg_or_orderblock=1434
- **EVAL::STANDARD** (total=1330800): momentum_reject=348725, basic_filters_failed=331037, adx_reject=266783, ema_alignment_reject=189454, sweeps_not_detected=165684, rsi_reject=20335, macd_reject=5971, invalid_sl_geometry=2811
- **EVAL::TREND_PULLBACK** (total=1395570): regime_blocked=469755, basic_filters_failed=277924, ema_alignment_reject=271200, ema_not_tested_prev=245232, body_conviction_fail=60699, no_ema_reclaim_close=33419, rsi_reject=30831, prev_already_above_emas=3310, prev_already_below_emas=1741, no_prev_high_break=882, no_prev_low_break=296, ema21_not_tagged=280, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1398731): breakout_not_found=551450, basic_filters_failed=349681, retest_proximity_failed=314725, regime_blocked=162695, volume_spike_missing=19861, ema_alignment_reject=312, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=1398749): momentum_reject=1236054, regime_blocked=162695

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1010128 | 61.1% |
| QUIET | 395034 | 23.9% |
| VOLATILE | 159923 | 9.7% |
| TRENDING_DOWN | 87712 | 5.3% |
| RANGING | 33 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1068**
- Average confidence gap to threshold: **16.99** (samples=1068) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=296, LINKUSDT=246, WIFUSDT=187, TRXUSDT=169, SOLUSDT=56, ZENUSDT=17, TONUSDT=15, WLFIUSDT=13, XAUUSDT=10, CLUSDT=9

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 13 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | watchlist_tier_keep | 123 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 18611 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 223 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1652 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 822 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 10998 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1195 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 589 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 150 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 4 |
| SR_FLIP_RETEST | filtered | min_confidence | 28884 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 628 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 1813 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 353 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 13 | 56.90 | 70.77 | 13.87 | 21.93 | 20.00 | 17.00 | 0.31 | 1.37 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 123 | 53.00 | 50.00 | -3.00 | 22.64 | 20.00 | 17.00 | 0.00 | 8.00 |
| FAILED_AUCTION_RECLAIM | filtered | 18834 | 61.09 | 72.21 | 11.12 | 23.00 | 18.35 | 14.00 | 3.39 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 2474 | 65.37 | 60.02 | -5.35 | 22.88 | 19.41 | 14.00 | 4.22 | 1.77 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11065 | 71.96 | 79.91 | 7.95 | 21.10 | 19.57 | 15.20 | 2.92 | 0.01 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1195 | 66.49 | 65.00 | -1.49 | 21.70 | 19.10 | 15.20 | 5.28 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 739 | 67.45 | 76.96 | 9.51 | 21.73 | 18.69 | 15.82 | 0.00 | 0.94 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 69.30 | 65.00 | -4.30 | 20.68 | 19.82 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 29512 | 56.39 | 73.74 | 17.35 | 21.36 | 19.99 | 15.20 | 1.45 | 4.70 |
| SR_FLIP_RETEST | kept | 2166 | 56.65 | 52.45 | -4.20 | 21.01 | 20.00 | 15.20 | 1.54 | 5.43 |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 80.00 | 1.00 | 21.50 | 17.80 | 18.00 | 5.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 13 | 56.90 | 21.15 | 18.00 | 3.46 | 13.54 | 5.42 | 7.46 | 0.31 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 123 | 53.00 | 15.00 | 18.00 | 3.00 | 10.00 | 5.00 | 10.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 18834 | 61.09 | 24.78 | 14.00 | 3.07 | 10.83 | 5.00 | 5.52 | 3.39 |
| FAILED_AUCTION_RECLAIM | kept | 2474 | 65.37 | 24.73 | 14.00 | 3.10 | 9.69 | 5.13 | 6.34 | 4.22 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11065 | 71.96 | 24.74 | 14.11 | 3.01 | 12.06 | 8.37 | 6.80 | 2.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1195 | 66.49 | 17.01 | 14.00 | 3.00 | 12.00 | 8.50 | 6.70 | 5.28 |
| QUIET_COMPRESSION_BREAK | filtered | 739 | 67.45 | 17.12 | 18.00 | 6.28 | 13.95 | 8.56 | 7.44 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 69.30 | 17.00 | 18.00 | 3.75 | 14.00 | 7.62 | 8.93 | 0.00 |
| SR_FLIP_RETEST | filtered | 29512 | 56.39 | 17.95 | 17.65 | 3.48 | 12.21 | 6.87 | 7.80 | 1.45 |
| SR_FLIP_RETEST | kept | 2166 | 56.65 | 18.80 | 18.00 | 3.13 | 12.17 | 6.34 | 7.83 | 1.54 |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 17.00 | 18.00 | 6.00 | 14.00 | 8.50 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 13 | 56.90 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | **0.37** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 123 | 53.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 18834 | 61.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | **0.01** |
| FAILED_AUCTION_RECLAIM | kept | 2474 | 65.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11065 | 71.96 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.01** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1195 | 66.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 739 | 67.45 | 0.04 | 0.00 | 0.02 | 0.00 | 0.88 | 0.00 | **0.94** |
| QUIET_COMPRESSION_BREAK | kept | 4 | 69.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 29512 | 56.39 | 0.00 | 0.00 | 0.01 | 0.00 | 0.18 | 0.00 | **0.19** |
| SR_FLIP_RETEST | kept | 2166 | 56.65 | 0.00 | 0.00 | 1.82 | 0.00 | 0.00 | 0.00 | **1.82** |
| TREND_PULLBACK_EMA | filtered | 2 | 79.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=9 (45.0%) | PREMATURE=0 (0.0%) | NEUTRAL=11 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 9 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 1 | 0 | 3 | 0 |
| momentum_loss | 5 | 0 | 6 | 0 |
| regime_shift | 3 | 0 | 2 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 0 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 0 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 2 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 4 | 0 | 8 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `7983187`
- `Path funnel` emissions: `226`
- `Regime distribution` emissions: `226`
- `QUIET_SCALP_BLOCK` events: `1068`
- `confidence_gate` events: `66127`
- `free_channel_post` events: `32`
- `pre_tp_fire` events: `3`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **3**
- Avg resolved threshold: **0.200%** raw → avg net **+1.30%** @ 10x
- Avg time-to-fire from dispatch: **348s**
- By threshold source: stamped=3

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 3 | 0.200% | +1.30% | 348 | stamped=3 |
- Top symbols: SOLUSDT=2, DOGEUSDT=1

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **32**

| Source | Count |
|---|---:|
| signal_close | 21 |
| regime_shift | 8 |
| pre_tp | 3 |

- By severity: HIGH=32

## Dependency readiness
- cvd: presence[absent=25942, present=1372807] state[empty=25942, populated=1372807] buckets[many=835744, none=25942, some=537063] sources[none] quality[none]
- funding_rate: presence[absent=10061, present=1388688] state[empty=10061, populated=1388688] buckets[few=1388688, none=10061] sources[none] quality[none]
- liquidation_clusters: presence[absent=1398749] state[empty=1398749] buckets[none=1398749] sources[none] quality[none]
- oi_snapshot: presence[absent=62, present=1398687] state[empty=62, populated=1398687] buckets[few=187, many=1397411, none=62, some=1089] sources[none] quality[none]
- order_book: presence[absent=70275, present=1328474] state[populated=1328474, unavailable=70275] buckets[few=1328474, none=70275] sources[book_ticker=1328474, unavailable=70275] quality[none=70275, top_of_book_only=1328474]
- orderblocks: presence[absent=1398749] state[empty=1398749] buckets[none=1398749] sources[not_implemented=1398749] quality[none]
- recent_ticks: presence[absent=115174, present=1283575] state[empty=115174, populated=1283575] buckets[many=1283575, none=115174] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.543060064315796` sec
- Median create→first breach: `32.331786155700684` sec
- Median create→terminal: `601.4577510356903` sec
- Median first breach→terminal: `0.3025491237640381` sec
- Fast-failure buckets: `{"under_120s": {"count": 20, "pct": 95.2}, "under_180s": {"count": 20, "pct": 95.2}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 20, "pct": 95.2}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 16 | 16 | 0.0 | 81.2 | 0.0 | -0.6486 | 32.45441913604736 | 33.53497505187988 |
| LIQUIDITY_SWEEP_REVERSAL | 8 | 8 | 0.0 | 87.5 | 0.0 | -0.9285 | 32.07015109062195 | 32.501352071762085 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.0 | 0.0 | 0.0 | 0.0019 | None | 740.7543185949326 |
| SR_FLIP_RETEST | 15 | 15 | 0.0 | 0.0 | 0.0 | 0.034 | 853.9284439086914 | 609.9341509342194 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 79065 | 47 | 19742 | 0.0 | 0.0 | 853.9284439086914 | 609.9341509342194 | 59323 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3179 | 0 | 3177 | 0.0 | 0.0 | None | None | 2 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-54`
- Gating Δ: `-95663`
- No-generation Δ: `-1867244`
- Fast failures Δ: `20`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.6486, "current_avg_pnl": -0.6486, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.9285, "current_avg_pnl": -0.9285, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0019, "current_avg_pnl": 0.0019, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.034, "current_avg_pnl": 0.034, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -67, "geometry_changed_delta": 0, "geometry_preserved_delta": 23786, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 853.93, "median_terminal_delta_sec": 609.93, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 2, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
