# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `851` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 402 | 402 | 395 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 3177 | 3177 | 2900 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1802 | 1802 | 1801 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1474564 | 1474162 | 402 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1474564 | 1471387 | 3177 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1474564 | 1472762 | 1802 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1474564 | 1384302 | 90262 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1474564 | 1474564 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1474564 | 1474564 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1474564 | 1474564 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1474564 | 1474564 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1474564 | 1474564 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1474564 | 1448982 | 25582 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1474564 | 1386968 | 87596 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1474564 | 1379412 | 95152 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 1474564 | 1472758 | 1806 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1474564 | 1474283 | 281 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1474564 | 1474564 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 90262 | 90262 | 42356 | 18 | active-low-quality (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 95152 | 95152 | 73284 | 5 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 25582 | 25582 | 3079 | 35 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 87596 | 87596 | 10508 | 36 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1806 | 1806 | 1798 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 281 | 281 | 9 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1474162): breakout_not_found=782218, basic_filters_failed=514827, retest_proximity_failed=168067, volume_spike_missing=8751, missing_fvg_or_orderblock=299
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1471387): regime_blocked=767720, basic_filters_failed=225267, sweeps_not_detected=222729, ema_alignment_reject=217201, adx_reject=33516, momentum_reject=4266, reclaim_confirmation_failed=357, rsi_reject=331
- **EVAL::DIVERGENCE_CONTINUATION** (total=1472762): regime_blocked=767720, cvd_divergence_failed=372495, basic_filters_failed=225267, retest_proximity_failed=40129, cvd_insufficient=34112, ema_alignment_reject=27244, missing_cvd=5794, missing_fvg_or_orderblock=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1384302): auction_not_detected=565595, basic_filters_failed=507181, reclaim_hold_failed=162118, tail_too_small=94005, regime_blocked=54341, rsi_reject=1062
- **EVAL::FUNDING_EXTREME** (total=1474564): funding_not_extreme=920913, basic_filters_failed=510401, rsi_reject=16872, missing_funding_rate=13665, ema_alignment_reject=10548, momentum_reject=1320, cvd_divergence_failed=845
- **EVAL::LIQUIDATION_REVERSAL** (total=1474564): cascade_threshold_not_met=958350, basic_filters_failed=514827, rsi_reject=755, cvd_divergence_failed=631, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1474564): no_ma_cross=959737, basic_filters_failed=514827
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1474564): feature_disabled=1474564
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1474564): regime_blocked=767720, breakout_not_found=230860, basic_filters_failed=225267, ema_alignment_reject=217201, adx_reject=33516
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1448982): regime_blocked=761185, basic_filters_failed=281914, breakout_not_detected=227215, compression_not_detected=152497, rsi_reject=17138, macd_reject=5873, missing_fvg_or_orderblock=3160
- **EVAL::SR_FLIP_RETEST** (total=1386968): basic_filters_failed=507181, retest_out_of_zone=399063, flip_close_not_confirmed=229457, reclaim_hold_failed=165637, regime_blocked=54341, wick_quality_failed=14141, missing_fvg_or_orderblock=8034, rsi_reject=6095, ema_alignment_reject=3019
- **EVAL::STANDARD** (total=1379412): basic_filters_failed=458020, momentum_reject=273533, adx_reject=259857, sweeps_not_detected=199000, ema_alignment_reject=138723, macd_reject=29702, invalid_sl_geometry=10434, rsi_reject=9855, htf_ema_reject=288
- **EVAL::TREND_PULLBACK** (total=1472758): regime_blocked=767720, basic_filters_failed=225267, ema_alignment_reject=217201, ema_not_tested_prev=180432, body_conviction_fail=51198, rsi_reject=13626, no_ema_reclaim_close=12700, prev_already_above_emas=2634, prev_already_below_emas=1262, no_prev_high_break=572, no_prev_low_break=134, momentum_flat=7, ema21_not_tagged=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1474283): breakout_not_found=627682, basic_filters_failed=514827, retest_proximity_failed=304765, volume_spike_missing=26995, missing_fvg_or_orderblock=13, ema_alignment_reject=1
- **EVAL::WHALE_MOMENTUM** (total=1474564): momentum_reject=1474564

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 847057 | 45.2% |
| QUIET | 838144 | 44.7% |
| TRENDING_DOWN | 71598 | 3.8% |
| VOLATILE | 64512 | 3.4% |
| RANGING | 54628 | 2.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **873**
- Average confidence gap to threshold: **8.00** (samples=873) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=411, WIFUSDT=329, NATGASUSDT=50, ZECUSDT=25, TONUSDT=14, ETHUSDT=9, XAUUSDT=8, SOLUSDT=6, XRPUSDT=6, LABUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 15917 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 472 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 20823 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 284 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 18110 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 339 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 15957 |
| SR_FLIP_RETEST | filtered | min_confidence | 15081 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 60 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 224 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 271 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 72.00 | 65.00 | -7.00 | 20.10 | 20.00 | 17.00 | 0.00 | -3.00 |
| FAILED_AUCTION_RECLAIM | filtered | 16389 | 60.43 | 65.00 | 4.57 | 22.93 | 18.07 | 14.00 | 3.51 | 5.79 |
| FAILED_AUCTION_RECLAIM | kept | 20823 | 68.00 | 65.00 | -3.00 | 22.95 | 20.00 | 14.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 286 | 54.05 | 65.00 | 10.95 | 23.99 | 17.44 | 15.20 | 0.07 | 11.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 18110 | 66.31 | 65.00 | -1.31 | 21.75 | 19.10 | 15.20 | 5.09 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 339 | 54.69 | 65.00 | 10.31 | 20.99 | 19.69 | 15.80 | 0.00 | 4.36 |
| QUIET_COMPRESSION_BREAK | kept | 15957 | 73.74 | 65.00 | -8.74 | 20.88 | 18.10 | 15.80 | 0.00 | -0.00 |
| SR_FLIP_RETEST | filtered | 15141 | 56.31 | 65.00 | 8.69 | 21.98 | 19.98 | 15.21 | 1.30 | 7.13 |
| SR_FLIP_RETEST | kept | 224 | 68.59 | 65.00 | -3.59 | 22.11 | 19.99 | 16.12 | 1.72 | 8.36 |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 65.00 | -4.20 | 22.60 | 19.20 | 20.00 | 4.00 | 1.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 271 | 55.50 | 65.00 | 9.50 | 24.03 | 16.60 | 20.00 | 1.50 | 12.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 72.00 | 25.00 | 18.00 | 3.00 | 11.00 | 5.00 | 10.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 16389 | 60.43 | 24.70 | 14.14 | 3.01 | 11.15 | 5.00 | 5.30 | 3.51 |
| FAILED_AUCTION_RECLAIM | kept | 20823 | 68.00 | 25.00 | 14.27 | 3.03 | 9.00 | 5.00 | 6.71 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 286 | 54.05 | 17.03 | 19.92 | 3.01 | 11.16 | 4.95 | 9.93 | 0.07 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 18110 | 66.31 | 17.00 | 14.00 | 3.00 | 12.00 | 8.50 | 6.70 | 5.09 |
| QUIET_COMPRESSION_BREAK | filtered | 339 | 54.69 | 17.24 | 18.00 | 11.70 | 14.05 | 8.33 | 4.47 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 15957 | 73.74 | 24.17 | 17.81 | 3.34 | 14.30 | 8.56 | 5.56 | 0.00 |
| SR_FLIP_RETEST | filtered | 15141 | 56.31 | 16.66 | 17.96 | 3.67 | 12.10 | 7.55 | 8.27 | 1.30 |
| SR_FLIP_RETEST | kept | 224 | 68.59 | 20.75 | 17.96 | 9.05 | 12.67 | 5.03 | 9.83 | 1.72 |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 4.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 271 | 55.50 | 17.00 | 20.00 | 3.00 | 11.00 | 5.00 | 10.00 | 1.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 16389 | 60.43 | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.00 | **0.02** |
| FAILED_AUCTION_RECLAIM | kept | 20823 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 286 | 54.05 | 0.00 | 0.00 | 11.92 | 0.00 | 0.00 | 0.00 | **11.92** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 18110 | 66.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 339 | 54.69 | 0.00 | 0.00 | 0.13 | 0.00 | 4.11 | 0.00 | **4.24** |
| QUIET_COMPRESSION_BREAK | kept | 15957 | 73.74 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 15141 | 56.31 | 0.00 | 0.00 | 0.46 | 0.00 | 0.01 | 0.00 | **0.47** |
| SR_FLIP_RETEST | kept | 224 | 68.59 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.04** |
| TREND_PULLBACK_EMA | kept | 1 | 69.20 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.80** |
| VOLUME_SURGE_BREAKOUT | filtered | 271 | 55.50 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=29 (76.3%) | PREMATURE=2 (5.3%) | NEUTRAL=7 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=3
- **Net-helping** — invalidation saved on 27 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 3 | 0 | 1 | 0 |
| other | 5 | 0 | 5 | 0 |
| regime_shift | 21 | 2 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 1 | 2 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 21 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 6 | 0 | 5 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `9628846`
- `Path funnel` emissions: `255`
- `Regime distribution` emissions: `255`
- `QUIET_SCALP_BLOCK` events: `873`
- `confidence_gate` events: `87542`
- `free_channel_post` events: `27`
- `pre_tp_fire` events: `12`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **12**
- Avg resolved threshold: **0.371%** raw → avg net **+3.01%** @ 10x
- Avg time-to-fire from dispatch: **604s**
- By threshold source: stamped=12

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 6 | 0.200% | +1.30% | 712 | stamped=6 |
| QUIET_COMPRESSION_BREAK | 3 | 0.409% | +3.38% | 298 | stamped=3 |
| FAILED_AUCTION_RECLAIM | 2 | 0.260% | +1.90% | 936 | stamped=2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1.503% | +14.33% | 212 | stamped=1 |
- Top symbols: CLUSDT=3, BTCUSDT=3, TONUSDT=1, LABUSDT=1, XRPUSDT=1, ZECUSDT=1, SOLUSDT=1, DOGEUSDT=1

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **27**

| Source | Count |
|---|---:|
| signal_close | 14 |
| pre_tp | 12 |
| regime_shift | 1 |

- By severity: HIGH=27

## Dependency readiness
- cvd: presence[absent=40598, present=1433966] state[empty=40598, populated=1433966] buckets[many=1132619, none=40598, some=301347] sources[none] quality[none]
- funding_rate: presence[absent=13665, present=1460899] state[empty=13665, populated=1460899] buckets[few=1460899, none=13665] sources[none] quality[none]
- liquidation_clusters: presence[absent=1474564] state[empty=1474564] buckets[none=1474564] sources[none] quality[none]
- oi_snapshot: presence[absent=8391, present=1466173] state[empty=8391, populated=1466173] buckets[few=237, many=1464590, none=8391, some=1346] sources[none] quality[none]
- order_book: presence[absent=71591, present=1402973] state[populated=1402973, unavailable=71591] buckets[few=1402973, none=71591] sources[book_ticker=1402973, unavailable=71591] quality[none=71591, top_of_book_only=1402973]
- orderblocks: presence[absent=1474564] state[empty=1474564] buckets[none=1474564] sources[not_implemented=1474564] quality[none]
- recent_ticks: presence[absent=110688, present=1363876] state[empty=110688, populated=1363876] buckets[many=1363876, none=110688] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.084153175354004` sec
- Median create→first breach: `858.8451170921326` sec
- Median create→terminal: `665.2517349720001` sec
- Median first breach→terminal: `0.719867467880249` sec
- Fast-failure buckets: `{"under_120s": {"count": 3, "pct": 30.0}, "under_180s": {"count": 3, "pct": 30.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 20.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0113 | None | 609.8221759796143 |
| FAILED_AUCTION_RECLAIM | 8 | 8 | 0.0 | 12.5 | 0.0 | 0.0717 | 896.6341761350632 | 922.8752094507217 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 33.3 | 0.0 | -0.5167 | 380.06766152381897 | 381.7530280351639 |
| QUIET_COMPRESSION_BREAK | 29 | 29 | 0.0 | 0.0 | 0.0 | -0.1271 | 434.083319067955 | 606.6282194852829 |
| SR_FLIP_RETEST | 28 | 28 | 0.0 | 0.0 | 0.0 | 0.1183 | 882.0779721736908 | 982.4777908325195 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | -1.5369 | 888.8814311027527 | 889.1060070991516 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 87596 | 36 | 10508 | 0.0 | 0.0 | 882.0779721736908 | 982.4777908325195 | 77088 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1806 | 1 | 1798 | 0.0 | 100.0 | 888.8814311027527 | 889.1060070991516 | 8 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `9`
- Gating Δ: `-5222`
- No-generation Δ: `1367441`
- Fast failures Δ: `3`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0717, "current_avg_pnl": 0.0717, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.5167, "current_avg_pnl": -0.5167, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1271, "current_avg_pnl": -0.1271, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1183, "current_avg_pnl": 0.1183, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -11, "geometry_changed_delta": 0, "geometry_preserved_delta": 17451, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 882.08, "median_terminal_delta_sec": 982.48, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 6, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 888.88, "median_terminal_delta_sec": 889.11, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
